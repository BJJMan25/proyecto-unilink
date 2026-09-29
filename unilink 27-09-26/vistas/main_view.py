import customtkinter as ctk
from tkinter import ttk, messagebox
from config import ICON_PATH
from vistas.usuario_view import UsuariosView
from vistas.producto_view import ProductoView
from vistas.inventario_view import VistaInventario
from vistas.ventas_view import VistaVentas
from vistas.ajustes_view import VistaAjustes
from controladores.producto_controller import ProductoController
from controladores.venta_controller import VentaController

from unilink_pos.views.dashboard_view import DashboardView
from unilink_pos.views.usuario_view import UsuarioView
from unilink_pos.views.venta_view import VentaView


class MainView(ctk.CTk):
    def __init__(self, usuario_controller):
        super().__init__()

        self.usuario_controller = usuario_controller
        self.usuario = usuario_controller.usuario_actual

        self.producto_controller = ProductoController()
        self.venta_controller = VentaController(self.usuario.id, self.usuario.nombre_completo)

        self.title("Unilink POS")
        self.geometry("1500x900")
        self.minsize(1100, 700)
        self.resizable(True, True)
        self.configure(fg_color="#F4F6F8")
        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1F2B2F")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="#F4F6F8")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.main_panel = ctk.CTkFrame(self.content, fg_color="#F4F6F8")
        self.main_panel.grid(row=0, column=0, sticky="nsew", padx=(16, 16), pady=(16, 20))
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.active_nav = None
        self.modular_enabled = True
        self.bind("<Configure>", self._ajustar_responsive)
        self._crear_sidebar()
        self._mostrar_dashboard()
        self.after(100, self._ajustar_responsive)

    def _ajustar_responsive(self, event=None):
        ancho_ventana = max(self.winfo_width(), 900)
        ancho_sidebar = min(260, max(200, ancho_ventana // 6))
        self.sidebar.configure(width=ancho_sidebar)

    @staticmethod
    def _inicio_label():
        return "Inicio"

    @staticmethod
    def _obtener_nav_items(rol_id):
        inicio = MainView._inicio_label()
        if rol_id == 1:
            return [
                (inicio, None),
                ("Usuarios", None),
                ("Inventario", None),
                ("Ventas", None),
            ]
        if rol_id == 2:
            return [
                (inicio, None),
                ("Inventario", None),
                ("Ventas", None),
            ]
        return [
            ("Ventas", None),
            ("Inventario", None),
        ]

    def _rol_nombre(self):
        rol_id = int(self.usuario.rol_id) if str(self.usuario.rol_id).isdigit() else self.usuario.rol_id
        if rol_id == 1:
            return "Administrador"
        if rol_id == 2:
            return "Supervisor"
        if rol_id == 3:
            return "Cajero"
        return getattr(self.usuario, "rol_nombre", "Usuario")

    def _crear_sidebar(self):
        self.sidebar.grid_columnconfigure(0, weight=1)

        avatar = ctk.CTkFrame(self.sidebar, width=72, height=72, corner_radius=36, fg_color="#D9E7E1")
        avatar.grid(row=0, column=0, pady=(24, 10))
        avatar.grid_propagate(False)
        ctk.CTkLabel(avatar, text="UJ", text_color="#123A2E", font=ctk.CTkFont(size=26, weight="bold")).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.sidebar, text="Unilink POS", text_color="#FFFFFF", font=ctk.CTkFont(size=22, weight="bold")).grid(row=1, column=0)
        ctk.CTkLabel(self.sidebar, text=self.usuario.nombre_completo, text_color="#CBD5E1", font=ctk.CTkFont(size=13)).grid(row=2, column=0)
        ctk.CTkLabel(self.sidebar, text=f"Rol: {self._rol_nombre()}", text_color="#B7C5CA", font=ctk.CTkFont(size=10)).grid(row=3, column=0, pady=(0, 20))

        rol_id = int(self.usuario.rol_id) if str(self.usuario.rol_id).isdigit() else self.usuario.rol_id
        inicio = self._inicio_label()
        if rol_id == 1:
            nav_items = [
                (inicio, self._mostrar_dashboard),
                ("Usuarios", self._mostrar_usuarios),
                ("Inventario", self._mostrar_productos),
                ("Ventas", self._mostrar_ventas),
                ("Ajustes", self._mostrar_ajustes),
            ]
            default_nav = inicio
        elif rol_id == 2:
            nav_items = [
                (inicio, self._mostrar_dashboard),
                ("Inventario", self._mostrar_productos),
                ("Ventas", self._mostrar_ventas),
            ]
            default_nav = inicio
        else:
            nav_items = [
                ("Ventas", self._mostrar_ventas),
                ("Inventario", self._mostrar_productos),
            ]
            default_nav = "Ventas"

        for idx, (label, command) in enumerate(nav_items, start=4):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                height=38,
                corner_radius=10,
                fg_color="#273A3F",
                hover_color="#324B50",
                text_color="#FFFFFF",
                border_width=0,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=command,
            )
            btn.grid(row=idx, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[label] = btn

        self.active_nav = default_nav
        self._set_active_nav(default_nav)

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.grid(row=100, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(100, weight=1)

        ctk.CTkButton(
            self.sidebar,
            text="Cerrar sesión",
            height=38,
            corner_radius=10,
            fg_color="#D95F5F",
            hover_color="#B94B4B",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._cerrar_sesion,
        ).grid(row=101, column=0, padx=14, pady=(0, 20), sticky="ew")

    def _limpiar_contenido(self):
        for widget in self.main_panel.winfo_children():
            widget.destroy()

    def _set_active_nav(self, label):
        self.active_nav = label
        for key, btn in self.nav_buttons.items():
            if key == label:
                btn.configure(
                    fg_color="#2FA572",
                    border_width=1,
                    border_color="#7BE0B3",
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="#273A3F",
                    border_width=0,
                    text_color="#DDEBF0"
                )

    def _card(self, parent, title, value, subtitle, accent="#2FA572"):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=title, text_color="#5E6C74", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        ctk.CTkLabel(card, text=value, text_color="#1A1A1A", font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=0, sticky="w", padx=16)
        ctk.CTkLabel(card, text=subtitle, text_color=accent, font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 16))
        return card

    def _mostrar_dashboard(self):
        self._limpiar_contenido()
        self._set_active_nav(self._inicio_label())

        if self.modular_enabled:
            dashboard = DashboardView(self.main_panel, usuario=self.usuario)
            dashboard.grid(row=0, column=0, sticky="nsew")
            return

        container = ctk.CTkFrame(self.main_panel, fg_color="#F4F6F8")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        rol_id = int(self.usuario.rol_id) if str(self.usuario.rol_id).isdigit() else self.usuario.rol_id
        if rol_id == 1:
            title = "Panel principal de administración"
            accent = "#2FA572"
            users = self.usuario_controller.obtener_usuarios() or []
            products = self.producto_controller.obtener_productos() or []
            stock_bajo = self.producto_controller.obtener_productos_stock_bajo(10)
            ventas_hoy = self.venta_controller.obtener_total_ventas_hoy()
            productos_en_stock = len(products) if products else 6
            stock_critico = max(2, min(len(stock_bajo) if stock_bajo else 2, 2))
            cards = [
                ("Ingresos del día", f"S/. {ventas_hoy:,.2f}", "+12.8% VS MES"),
                ("Usuarios activos", str(len(users)), "+24 este mes"),
                ("Productos en stock", str(productos_en_stock), f"{stock_critico} con stock bajo"),
            ]
            chart_rows = [
                ("Ventas", 84), ("Usuarios", 62), ("Inventario", 90), ("Cobranza", 70), ("Rendimiento", 78)
            ]
            activity = [
                ("Apertura de caja", "Cierre de jornada validado por admin"),
                ("Inventario", f"Se revisaron {stock_critico} productos con stock crítico"),
                ("Seguridad", "2 accesos registrados en auditoría"),
            ]
        elif rol_id == 2:
            title = "Panel del almacén"
            accent = "#3A8BDA"
            stock_bajo = self.producto_controller.obtener_productos_stock_bajo(10)
            products = self.producto_controller.obtener_productos() or []
            ventas_hoy = self.venta_controller.obtener_total_ventas_hoy()
            cards = [
                ("Stock total", str(sum(p.stock_actual for p in products)), "+146 unidades hoy"),
                ("Alertas", str(len(stock_bajo)), "Críticos por revisar"),
                ("Ventas del día", f"S/. {ventas_hoy:,.2f}", "+8.6% respecto a ayer"),
            ]
            chart_rows = [
                ("Entrada", 68), ("Salida", 72), ("Reabastecimiento", 86), ("Merma", 45), ("Disponibilidad", 82)
            ]
            activity = [
                ("Pedidos", "Se priorizan 6 productos por reabastecimiento"),
                ("Revisión", "Se validó el stock mínimo del almacén"),
                ("Ventas", "Se atendieron 18 tickets con movimiento de inventario"),
            ]
        else:
            title = "Panel de ventas"
            accent = "#E09F3E"
            products = self.producto_controller.obtener_productos() or []
            ventas_hoy = self.venta_controller.obtener_total_ventas_hoy()
            cards = [
                ("Ventas del turno", f"S/. {ventas_hoy:,.2f}", "+12 ventas hoy"),
                ("Productos disponibles", str(len(products)), "Inventario en línea"),
                ("Turno activo", "7h 40m", "Operativo"),
            ]
            chart_rows = [
                ("Efectivo", 76), ("Tarjeta", 58), ("Yape", 66), ("Ticket medio", 71), ("Cumplimiento", 80)
            ]
            activity = [
                ("Caja", "Se cerró una operación con saldo positivo"),
                ("Productos", "Se promocionaron 5 artículos con stock disponible"),
                ("Servicio", "El cliente atendido fue registrado correctamente"),
            ]

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, text_color="#1A1A1A", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")

        chip = ctk.CTkFrame(container, fg_color="#EAF8F2", corner_radius=12)
        chip.grid(row=0, column=0, sticky="e", padx=12)
        ctk.CTkLabel(chip, text=f"Rol real: {self._rol_nombre()}", text_color="#1C6C4C", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=12, pady=8)

        kpi_row = ctk.CTkFrame(container, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1)
        for idx, (title, value, subtitle) in enumerate(cards):
            card = ctk.CTkFrame(kpi_row, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 12, 0 if idx == 2 else 12))
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=title, text_color="#5E6C74", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
            ctk.CTkLabel(card, text=value, text_color="#1A1A1A", font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=0, sticky="w", padx=16)
            ctk.CTkLabel(card, text=subtitle, text_color=accent, font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 16))

        body = ctk.CTkFrame(container, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)

        left_panel = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(left_panel, text="Performance por indicador", text_color="#1A1A1A", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 12))

        for row_idx, (label, percentage) in enumerate(chart_rows, start=1):
            bar_frame = ctk.CTkFrame(left_panel, fg_color="#F6F9FB", corner_radius=10)
            bar_frame.grid(row=row_idx, column=0, sticky="ew", padx=18, pady=6)
            bar_frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(bar_frame, text=label, text_color="#1A1A1A", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))
            ctk.CTkLabel(bar_frame, text=f"{percentage}%", text_color=accent, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="e", padx=10, pady=(8, 4))
            progress = ctk.CTkProgressBar(bar_frame, orientation="horizontal", height=8)
            progress.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
            progress.set(percentage / 100)
            progress.configure(progress_color=accent)

        right_panel = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right_panel, text="Actividad reciente", text_color="#1A1A1A", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 14))
        for idx, (title, detail) in enumerate(activity, start=1):
            item = ctk.CTkFrame(right_panel, fg_color="#F7FAF9", corner_radius=12)
            item.grid(row=idx, column=0, sticky="ew", padx=18, pady=6)
            ctk.CTkLabel(item, text=title, text_color="#1A1A1A", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(item, text=detail, text_color="#5E6C74", font=ctk.CTkFont(size=10), wraplength=240).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        quick_actions = ["Abrir ventas", "Ver inventario", "Actualizar stock"]
        if rol_id == 1:
            quick_actions.append("Auditar usuarios")
        quick_panel = ctk.CTkFrame(container, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        quick_panel.grid(row=3, column=0, sticky="ew", padx=12, pady=(8, 0))
        quick_panel.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        ctk.CTkLabel(quick_panel, text="Entradas rápidas", text_color="#1A1A1A", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=5, sticky="w", padx=18, pady=(16, 12))
        for idx, action in enumerate(quick_actions):
            btn = ctk.CTkButton(
                quick_panel,
                text=action,
                height=34,
                corner_radius=10,
                fg_color="#EAF8F2",
                hover_color="#D9F1E6",
                text_color="#1A1A1A",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda a=action: self._quick_action(a)
            )
            btn.grid(row=1, column=idx, sticky="ew", padx=8, pady=(0, 20))

        self.quick_entry_frame = ctk.CTkFrame(container, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        self.quick_entry_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(12, 20))
        self.quick_entry_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.quick_entry_frame, text="Acceso rápido", text_color="#1A1A1A", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 8))

        self.quick_search = ctk.CTkEntry(
            self.quick_entry_frame,
            placeholder_text="Buscar producto por código o nombre",
            height=38,
            fg_color="#F4F6F8",
            border_color="#DCE5E8",
            text_color="#1A1A1A",
        )
        self.quick_search.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.quick_search.bind("<Return>", lambda event: self._buscar_rapido())

        ctk.CTkButton(
            self.quick_entry_frame,
            text="Buscar",
            width=120,
            height=36,
            corner_radius=10,
            fg_color="#2FA572",
            hover_color="#248963",
            command=self._buscar_rapido,
        ).grid(row=2, column=0, sticky="e", padx=18, pady=(0, 16))

    def _quick_action(self, action):
        if action == "Abrir ventas":
            self._mostrar_ventas()
        elif action == "Ver inventario":
            self._mostrar_productos()
        elif action == "Actualizar stock":
            self._mostrar_productos()
        elif action == "Auditar usuarios":
            if self.usuario.rol_id == 1:
                self._mostrar_usuarios()
            else:
                messagebox.showwarning("Permiso", "Solo el administrador puede auditar usuarios.")

    def _buscar_rapido(self):
        texto = self.quick_search.get().strip()
        if not texto:
            messagebox.showwarning("Búsqueda", "Escribe un código o nombre para buscar.")
            return
        self._mostrar_productos()
        try:
            view = self.main_panel.winfo_children()[0]
            if hasattr(view, "entry_busqueda"):
                view.entry_busqueda.delete(0, "end")
                view.entry_busqueda.insert(0, texto)
                view._filtrar_tabla()
        except Exception:
            pass

    def _mostrar_usuarios(self):
        rol_id = int(self.usuario.rol_id) if str(self.usuario.rol_id).isdigit() else self.usuario.rol_id
        if rol_id != 1:
            messagebox.showwarning("Permiso", "Solo el administrador puede gestionar usuarios.")
            return
        self._limpiar_contenido()
        self._set_active_nav("Usuarios")
        UsuariosView(self.main_panel, self.usuario_controller).grid(row=0, column=0, sticky="nsew")

    def _mostrar_productos(self):
        self._limpiar_contenido()
        self._set_active_nav("Inventario")
        VistaInventario(self.main_panel, usuario=self.usuario).grid(row=0, column=0, sticky="nsew")

    def _mostrar_ventas(self):
        self._limpiar_contenido()
        self._set_active_nav("Ventas")
        if self.modular_enabled:
            VentaView(self.main_panel).grid(row=0, column=0, sticky="nsew")
            return
        VistaVentas(self.main_panel, usuario=self.usuario).grid(row=0, column=0, sticky="nsew")

    def _mostrar_ajustes(self):
        self._limpiar_contenido()
        self._set_active_nav("Ajustes")
        VistaAjustes(self.main_panel, usuario=self.usuario).grid(row=0, column=0, sticky="nsew")

    def _cerrar_sesion(self):
        self.usuario_controller.cerrar_sesion()
        self.destroy()

        from vistas.login_view import LoginView
        app = LoginView(self.usuario_controller)
        app.mainloop()