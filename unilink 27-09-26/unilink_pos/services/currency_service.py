import threading
import time
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from bs4 import BeautifulSoup
from mysql.connector import Error as MySQLError

from unilink_pos.config.conexion import get_db_connection


class CurrencyService:
    """Servicio de actualización y fallback para la tasa de cambio USD/VES."""

    def __init__(self, refresh_hours: int = 6, host: str = "localhost", user: str = "root", password: str = "", database: str = "unilink_pos"):
        self.refresh_hours = max(1, refresh_hours)
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self._stop_event = threading.Event()
        self._thread = None

    @staticmethod
    def _fetch_from_public_api():
        endpoints = [
            "https://api.exchangerate.host/convert?from=USD&to=VES",
            "https://open.er-api.com/v6/latest/USD",
        ]

        for url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                payload = response.json()
                if "result" in payload and payload.get("result"):
                    return Decimal(str(payload["result"]))
                if "rates" in payload and payload["rates"].get("VES"):
                    return Decimal(str(payload["rates"]["VES"]))
            except Exception:
                continue

        try:
            response = requests.get("https://www.bcv.org.ve/", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for text in soup.stripped_strings:
                if "USD" in text.upper() or "DÓLAR" in text.upper():
                    numbers = [part for part in text.replace(",", ".").split() if part.replace(".", "", 1).isdigit()]
                    if numbers:
                        return Decimal(numbers[0])
        except Exception:
            pass

        raise ConnectionError("No se pudo consultar la tasa oficial desde la red.")

    @staticmethod
    def obtener_tasa_actual():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT valor FROM tasas_cambio ORDER BY fecha_actualizacion DESC LIMIT 1",
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return Decimal(str(row["valor"]))
        return None

    @staticmethod
    def guardar_tasa(valor: Decimal, fuente: str = "API"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasas_cambio (moneda_origen, moneda_destino, valor, fuente, fecha_actualizacion) VALUES (%s, %s, %s, %s, NOW())",
            ("USD", "VES", str(valor), fuente),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return valor

    def sincronizar_tasa(self):
        ultima = self.obtener_tasa_actual()
        try:
            valor = self._fetch_from_public_api()
            if valor <= 0:
                raise ValueError("La tasa debe ser positiva.")
            self.guardar_tasa(valor, fuente="API")
            return valor, True, "Actualización automática correcta."
        except Exception:
            if ultima is not None:
                return ultima, False, "Usando última tasa guardada por falta de conexión."
            return None, False, "Sin conexión y sin tasa previa disponible."

    def actualizar_manual(self, valor: float, usuario_id: int = None):
        try:
            tasa = Decimal(str(valor))
        except InvalidOperation:
            return False, "Valor inválido."

        if tasa <= 0:
            return False, "La tasa debe ser mayor que cero."

        self.guardar_tasa(tasa, fuente="Manual")
        return True, "Tasa actualizada manualmente."

    def start_background_sync(self, interval_hours: int | None = None):
        if interval_hours is not None:
            self.refresh_hours = max(1, interval_hours)
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()

    def stop_background_sync(self):
        self._stop_event.set()

    def _background_loop(self):
        while not self._stop_event.is_set():
            self.sincronizar_tasa()
            for _ in range(self.refresh_hours * 3600):
                if self._stop_event.is_set():
                    return
                time.sleep(1)

    @staticmethod
    def convertir_a_local(monto_usd: float):
        tasa = CurrencyService.obtener_tasa_actual()
        if tasa is None:
            raise ValueError("No hay tasa guardada para convertir.")
        return float(Decimal(str(monto_usd)) * tasa)

    @staticmethod
    def convertir_a_usd(monto_local: float):
        tasa = CurrencyService.obtener_tasa_actual()
        if tasa is None:
            raise ValueError("No hay tasa guardada para convertir.")
        return float(Decimal(str(monto_local)) / tasa)


class ConversorMoneda(CurrencyService):
    """Helper estático para conversiones en tiempo real."""

    @staticmethod
    def obtener_tasa_actual():
        return CurrencyService.obtener_tasa_actual()

    @staticmethod
    def convertir_a_local(monto_usd: float):
        return CurrencyService.convertir_a_local(monto_usd)

    @staticmethod
    def convertir_a_usd(monto_local: float):
        return CurrencyService.convertir_a_usd(monto_local)
