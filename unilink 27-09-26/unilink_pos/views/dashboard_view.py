import customtkinter as ctk
from tkinter import ttk

from unilink_pos.config.conexion import get_db_connection


class DashboardView(ctk.CTkFrame):
    """Vista principal del dashboard con KPI y actividad."""

    def __init__(self, parent, usuario=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.usuario = usuario
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_kpis()
        self._build_activity()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Dashboard principal",
            text_color="#111827",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

    def _build_kpis(self):
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        sales = self._get_sales_today()
        users = self._get_active_users()
        stock = self._get_stock_alerts()

        self._kpi_card(cards, "Ventas del día", f"S/ {sales:.2f}", "+8.6% vs. ayer", 0)
        self._kpi_card(cards, "Usuarios activos", str(users), "Sin incidencias", 1)
        self._kpi_card(cards, "Alertas stock", str(stock), "Revisar inventario", 2)

    def _kpi_card(self, parent, title, value, subtitle, col):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        card.grid(row=0, column=col, padx=(0, 12) if col != 2 else (12, 0), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=title, text_color="#64748B", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        ctk.CTkLabel(card, text=value, text_color="#111827", font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=0, sticky="w", padx=16)
        ctk.CTkLabel(card, text=subtitle, text_color="#2FA572", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 16))

    def _build_activity(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Performance por indicador", text_color="#111827", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        for index, (label, value) in enumerate([("Ventas", 82), ("Inventario", 68), ("Cobros", 91), ("Seguridad", 75)], start=1):
            bar = ctk.CTkFrame(left, fg_color="#F6F9FB", corner_radius=10)
            bar.grid(row=index, column=0, sticky="ew", padx=18, pady=6)
            bar.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(bar, text=label, text_color="#111827", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))
            ctk.CTkLabel(bar, text=f"{value}%", text_color="#2FA572", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="e", padx=10, pady=(8, 4))
            progress = ctk.CTkProgressBar(bar, orientation="horizontal", height=8)
            progress.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
            progress.set(value / 100)

        right = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="Actividad reciente", text_color="#111827", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        logs = self._get_recent_activity()
        for idx, row in enumerate(logs[:4], start=1):
            item = ctk.CTkFrame(right, fg_color="#F7FAF9", corner_radius=12)
            item.grid(row=idx, column=0, sticky="ew", padx=18, pady=6)
            ctk.CTkLabel(item, text=row["accion"], text_color="#111827", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(item, text=row["descripcion"], text_color="#64748B", font=ctk.CTkFont(size=10), wraplength=220).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    def _get_sales_today(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE DATE(fecha) = CURDATE()")
        value = cursor.fetchone()[0] or 0
        cursor.close(); conn.close()
        return float(value)

    def _get_active_users(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE estado = 1")
        value = cursor.fetchone()[0] or 0
        cursor.close(); conn.close()
        return int(value)

    def _get_stock_alerts(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
        value = cursor.fetchone()[0] or 0
        cursor.close(); conn.close()
        return int(value)

    def _get_recent_activity(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT accion, descripcion FROM logs_auditoria ORDER BY fecha DESC LIMIT 4")
        rows = cursor.fetchall()
        cursor.close(); conn.close()
        return rows
