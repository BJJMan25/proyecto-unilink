import threading
import time
from decimal import Decimal, InvalidOperation
from typing import Optional

import mysql.connector
import requests
from bs4 import BeautifulSoup


class CurrencyService:
    """Servicio central para consultar, guardar y sincronizar la tasa de cambio."""

    def __init__(self, host: str = "localhost", user: str = "root", password: str = "", database: str = "unilink", refresh_interval_hours: int = 6):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.refresh_interval_seconds = max(60, refresh_interval_hours * 3600)
        self._stop_event = threading.Event()
        self._thread = None
        self._last_rate = None
        self._last_error = None
        self._ensure_schema()
        self._current_rate = self.obtener_tasa_actual()

    def _connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=True,
            connection_timeout=10,
        )

    def _ensure_schema(self):
        """Crea la tabla de tasas y valida la auditoría del sistema."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasas_cambio (
                    id_tasa INT AUTO_INCREMENT PRIMARY KEY,
                    moneda_origen VARCHAR(10) NOT NULL,
                    moneda_destino VARCHAR(10) NOT NULL,
                    valor DECIMAL(10,4) NOT NULL,
                    fuente VARCHAR(50) NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS logs_auditoria (
                    id_log INT AUTO_INCREMENT PRIMARY KEY,
                    accion VARCHAR(120) NOT NULL,
                    descripcion TEXT NOT NULL,
                    usuario_id INT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as exc:
            raise RuntimeError(f"No se pudo inicializar la base de datos de tasas: {exc}") from exc

    def _get_last_saved_rate(self) -> Optional[Decimal]:
        try:
            conn = self._connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT valor, fuente, fecha_actualizacion FROM tasas_cambio ORDER BY fecha_actualizacion DESC LIMIT 1"
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row is None:
                return None
            return Decimal(str(row["valor"]))
        except Exception:
            return None

    def _upsert_rate(self, valor: Decimal, fuente: str = "API", manual: bool = False) -> Decimal:
        anterior = self._get_last_saved_rate()
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasas_cambio (moneda_origen, moneda_destino, valor, fuente, fecha_actualizacion)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            ("USD", "VES", str(valor), fuente),
        )
        conn.commit()
        cursor.close()
        conn.close()

        if anterior is not None and abs((valor - anterior)) > Decimal("0.0001"):
            self._log_tasa_change(anterior, valor, fuente if manual else "Automática")
        elif anterior is None:
            self._log_tasa_change(Decimal("0.00"), valor, fuente if manual else "Automática")

        self._last_rate = valor
        self._current_rate = valor
        return valor

    def _log_tasa_change(self, anterior: Decimal, nuevo: Decimal, tipo: str):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs_auditoria (accion, descripcion, usuario_id, fecha) VALUES (%s, %s, %s, NOW())",
                (
                    "Tasa de cambio",
                    f"Valor anterior: {float(anterior):.4f}, nuevo: {float(nuevo):.4f}, tipo: {tipo}",
                    None,
                ),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error:
            pass

    def obtener_tasa_actual(self) -> Optional[Decimal]:
        """Obtiene la última tasa guardada en MySQL o la tasa vigente actual."""
        try:
            conn = self._connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT valor FROM tasas_cambio ORDER BY fecha_actualizacion DESC LIMIT 1"
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                self._last_rate = Decimal(str(row["valor"]))
                self._current_rate = self._last_rate
                return self._last_rate
        except mysql.connector.Error:
            pass

        if self._last_rate is not None:
            return self._last_rate
        return None

    def obtener_estado_tasa(self) -> tuple[str, Optional[Decimal], str]:
        """Retorna estado: actualizada_hoy, fallback o sin_conexion, junto con la tasa actual y texto legible."""
        tasa = self.obtener_tasa_actual()
        if tasa is None:
            return "sin_conexion", None, "Sin tasa guardada"
        return "actualizada_hoy", tasa, f"1 USD = {float(tasa):.2f} BS"

    def _consultar_api_publica(self) -> Decimal:
        urls = [
            "https://api.exchangerate.host/convert?from=USD&to=VES",
            "https://open.er-api.com/v6/latest/USD",
        ]
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                payload = response.json()
                if "result" in payload and payload.get("result"):
                    return Decimal(str(payload["result"]))
                if "rates" in payload and "VES" in payload["rates"]:
                    return Decimal(str(payload["rates"]["VES"]))
            except (requests.RequestException, ValueError, TypeError):
                continue

        # Fallback BCV / scrape local page.
        fallback_url = "https://www.bcv.org.ve/"
        response = requests.get(fallback_url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for match in soup.find_all(string=lambda s: s and "USD" in s.upper()):
            text = str(match)
            if "Dólar" in text or "USD" in text:
                numbers = [token for token in text.replace(",", ".").split() if token.replace(".", "", 1).isdigit()]
                if numbers:
                    return Decimal(numbers[0])

        raise ConnectionError("No se pudo obtener la tasa de cambio desde fuentes públicas.")

    def sincronizar_tasa(self, force: bool = False) -> tuple[Optional[Decimal], bool, str]:
        """Consulta la tasa del día y la persiste en MySQL. Si falla, mantiene la última tasa sin romper la app."""
        prev = self.obtener_tasa_actual()
        try:
            valor = self._consultar_api_publica()
            if valor <= 0:
                raise ValueError("La tasa obtenida debe ser mayor a cero.")
            self._upsert_rate(valor, fuente="API", manual=False)
            self._last_error = None
            return self._current_rate, True, "Actualización automática correcta"
        except Exception as exc:  # noqa: BLE001
            self._last_error = str(exc)
            if prev is not None:
                self._current_rate = prev
                return prev, False, "Usando última tasa guardada por falta de conexión"

            return None, False, "No hay conexión ni última tasa disponible"

    def actualizar_manual(self, valor: float, usuario_id: Optional[int] = None) -> tuple[bool, str, Optional[Decimal]]:
        """Registra un ajuste manual introducido por admin/empleador."""
        try:
            val = Decimal(str(valor))
        except InvalidOperation:
            return False, "El valor ingresado no es válido.", None
        if val <= 0:
            return False, "La tasa debe ser mayor que cero.", None

        tasa = self._upsert_rate(val, fuente="Manual", manual=True)
        return True, "Tasa actualizada manualmente correctamente.", tasa

    def start_background_sync(self, interval_hours: Optional[int] = None):
        if self._thread is not None and self._thread.is_alive():
            return
        if interval_hours is not None:
            self.refresh_interval_seconds = max(60, interval_hours * 3600)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._background_worker, daemon=True)
        self._thread.start()

    def stop_background_sync(self):
        self._stop_event.set()

    def _background_worker(self):
        while not self._stop_event.is_set():
            try:
                self.sincronizar_tasa(force=False)
            except Exception:
                pass
            for _ in range(int(self.refresh_interval_seconds)):
                if self._stop_event.is_set():
                    return
                time.sleep(1)


class ConversorMoneda:
    """Helper estático para convertir correctamente entre USD y local."""

    _service = CurrencyService()

    @staticmethod
    def obtener_tasa_actual() -> Decimal:
        tasa = ConversorMoneda._service.obtener_tasa_actual()
        if tasa is None:
            raise ValueError("No hay tasa de cambio disponible en la base de datos.")
        return tasa

    @staticmethod
    def convertir_a_local(monto_usd: float) -> float:
        tasa = ConversorMoneda.obtener_tasa_actual()
        return float(Decimal(str(monto_usd)) * tasa)

    @staticmethod
    def convertir_a_usd(monto_local: float) -> float:
        tasa = ConversorMoneda.obtener_tasa_actual()
        if tasa == 0:
            raise ValueError("La tasa actual es cero y no se puede convertir.")
        return float(Decimal(str(monto_local)) / tasa)


if __name__ == "__main__":
    service = CurrencyService()
    print(service.sincronizar_tasa())
