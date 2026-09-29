import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# =========================================
# Paleta obligatoria extraída del sistema
# =========================================
BG = "#ECECE9"
PANEL = "#F0F1EC"
SIDEBAR = "#4A5B6B"
SIDEBAR_ACTIVE = "#5E676E"
PRIMARY_START = "#2D4F6A"
PRIMARY_END = "#3A5771"
SUCCESS = "#56A77E"
SUCCESS_DARK = "#3A5A42"
INACTIVE = "#695123"
CRITICAL = "#6D352F"
CANCEL = "#8C8C8F"
TEXT = "#333333"
TEXT_LIGHT = "#FFFFFF"

def set_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def sidebar_buttons(parent, items, active_item):
    for idx, item in enumerate(items):
        active = item == active_item
        btn = ctk.CTkButton(
            parent,
            text=item,
            height=38,
            corner_radius=10,
            fg_color=SIDEBAR_ACTIVE if active else "transparent",
            hover_color=SIDEBAR_ACTIVE if active else "#55626F",
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        btn.grid(row=idx, column=0, sticky="ew", padx=12, pady=4)


def create_sidebar(frame, nombre, rol, activo):
    sidebar = ctk.CTkFrame(frame, width=260, fg_color=SIDEBAR, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)
    sidebar.grid_columnconfigure(0, weight=1)

    avatar = ctk.CTkFrame(sidebar, width=72, height=72, corner_radius=36, fg_color="#D8DDE3")
    avatar.grid(row=0, column=0, pady=(26, 8), padx=0)
    avatar.grid_propagate(False)
    avatar_label = ctk.CTkLabel(avatar, text="AJ", text_color="#4A5B6B", font=ctk.CTkFont(size=28, weight="bold"))
    avatar_label.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(sidebar, text=nombre, text_color=TEXT_LIGHT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=0, pady=(0, 2))
    ctk.CTkLabel(sidebar, text=rol, text_color="#E4E8EB", font=ctk.CTkFont(size=12)).grid(row=2, column=0)
    ctk.CTkLabel(sidebar, text="Online", text_color="#DDE7E1", font=ctk.CTkFont(size=10)).grid(row=3, column=0, pady=(0, 18))

    nav_items = ["Inicio", "Usuarios", "Inventario", "Ventas", "Reportes", "Configuración"]
    if activo == "Usuarios":
        nav_items = ["Inicio", "Usuarios", "Inventario", "Ventas", "Reportes", "Configuración"]
    elif activo == "Dashboard":
        nav_items = ["Dashboard", "Ventas", "Empleados", "Productos", "Reportes", "Configuración"]
    else:
        nav_items = ["Caja", "Productos", "Ventas", "Turnos", "Clientes", "Configuración"]

    nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    nav_frame.grid(row=4, column=0, sticky="nsew")
    nav_frame.grid_columnconfigure(0, weight=1)
    sidebar_buttons(nav_frame, nav_items, activo)

    spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
    spacer.grid(row=5, column=0, sticky="nsew")
    sidebar.grid_rowconfigure(5, weight=1)

    ctk.CTkButton(
        sidebar,
        text="Cerrar Sesión",
        height=38,
        fg_color=CRITICAL,
        hover_color="#552B2A",
        text_color=TEXT_LIGHT,
        font=ctk.CTkFont(size=13, weight="bold"),
        corner_radius=10,
    ).grid(row=6, column=0, padx=12, pady=(0, 20), sticky="ew")

    return sidebar


def kpi_card(parent, title, value, subtitle, accent="#2D4F6A"):
    card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E5E6E2")
    card.grid_columnconfigure(0, weight=1)
    card.grid_rowconfigure(0, weight=1)
    ctk.CTkLabel(card, text=title, text_color="#5B5B5B", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=16, pady=(18, 2))
    ctk.CTkLabel(card, text=value, text_color=TEXT, font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 2))
    ctk.CTkLabel(card, text=subtitle, text_color=accent, font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 18))
    return card


def admin_screen(parent):
    frame = ctk.CTkFrame(parent, fg_color=BG, corner_radius=24)
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    create_sidebar(frame, "Alberto Jaimes", "Administrador", "Usuarios")

    content = ctk.CTkFrame(frame, fg_color=BG, corner_radius=18)
    content.grid(row=0, column=1, sticky="nsew", padx=(16, 14), pady=14)
    content.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(header, text="Gestión de Usuarios", text_color=TEXT, font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
    ctk.CTkButton(header, text="＋ Registrar Usuario", height=38, corner_radius=10, fg_color=PRIMARY_START, hover_color=PRIMARY_END, text_color=TEXT_LIGHT, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="e")

    kpi_row = ctk.CTkFrame(content, fg_color="transparent")
    kpi_row.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
    kpi_row.grid_columnconfigure((0, 1, 2), weight=1)
    kpi_card(kpi_row, "Usuarios Totales", "1,248", "+12.4% este mes", "#2D4F6A").grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    kpi_card(kpi_row, "Roles Configurados", "6", "2 nuevos", "#3A5771").grid(row=0, column=1, sticky="nsew", padx=12)
    kpi_card(kpi_row, "Sesiones Hoy", "94", "+18.7% vs ayer", "#2D4F6A").grid(row=0, column=2, sticky="nsew", padx=(12, 0))

    table_container = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E3E4E0")
    table_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 12))
    table_container.grid_columnconfigure(0, weight=1)
    table_container.grid_rowconfigure(0, weight=1)

    columns = ("id", "nombre", "usuario", "rol", "estado", "fecha")
    table = ttk.Treeview(table_container, columns=columns, show="headings", height=10, selectmode="browse")
    table.heading("id", text="ID")
    table.heading("nombre", text="Nombre Completo")
    table.heading("usuario", text="Usuario")
    table.heading("rol", text="Rol")
    table.heading("estado", text="Estado")
    table.heading("fecha", text="Fecha de Creación")
    table.column("id", width=60, anchor="center")
    table.column("nombre", width=220, anchor="w")
    table.column("usuario", width=150, anchor="w")
    table.column("rol", width=110, anchor="center")
    table.column("estado", width=100, anchor="center")
    table.column("fecha", width=150, anchor="center")
    table.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 8))

    default_rows = [
        (1, "Diego Paredes", "diego.p", "Administrador", "Activo", "2026-09-08"),
        (2, "Laura Salazar", "laura.s", "Supervisor", "Activo", "2026-09-05"),
        (3, "Marco Quispe", "marco.q", "Empleado", "Inactivo", "2026-09-02"),
        (4, "Paula Rivera", "paula.r", "Empleado", "Activo", "2026-09-01"),
        (5, "Renzo Silva", "renzo.s", "Supervisor", "Activo", "2026-08-28"),
        (6, "Carmen Vega", "carmen.v", "Administrativo", "Inactivo", "2026-08-27"),
    ]
    for row in default_rows:
        table.insert("", "end", values=row)

    script_style = ttk.Style()
    script_style.configure("Treeview", rowheight=28, background=PANEL, fieldbackground=PANEL, foreground=TEXT)
    script_style.map("Treeview", background=[("selected", "#D9E3EB")], foreground=[("selected", TEXT)])
    script_style.configure("Treeview.Heading", background="#EBEEF0", foreground=TEXT, font=("Segoe UI", 10, "bold"))

    actions = ctk.CTkFrame(content, fg_color="transparent")
    actions.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 18))
    buttons = [
        ("Activar", PRIMARY_START, PRIMARY_END),
        ("Desactivar", CRITICAL, "#552B2A"),
        ("Editar", PRIMARY_START, PRIMARY_END),
        ("Cambiar Contraseña", PRIMARY_START, PRIMARY_END),
        ("Refrescar", CANCEL, "#676767"),
        ("Cerrar Sesión", CRITICAL, "#552B2A"),
    ]
    for idx, (label, color, hover) in enumerate(buttons):
        ctk.CTkButton(actions, text=label, width=140, height=36, corner_radius=10, fg_color=color, hover_color=hover, text_color=TEXT_LIGHT, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=idx, padx=(0, 8), sticky="ew")



def employer_screen(parent):
    frame = ctk.CTkFrame(parent, fg_color=BG, corner_radius=24)
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    create_sidebar(frame, "Marta Flores", "Empleador", "Dashboard")

    content = ctk.CTkFrame(frame, fg_color=BG, corner_radius=18)
    content.grid(row=0, column=1, sticky="nsew", padx=(16, 14), pady=14)
    content.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 8))
    ctk.CTkLabel(header, text="Panel Gerencial", text_color=TEXT, font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")

    kpi_row = ctk.CTkFrame(content, fg_color="transparent")
    kpi_row.grid(row=1, column=0, sticky="ew", padx=10, pady=6)
    kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
    kpi_card(kpi_row, "Ventas del Día", "S/. 14,280", "+8.6% vs ayer", PRIMARY_START).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    kpi_card(kpi_row, "Ingresos del Mes", "S/. 92,430", "+15.1%", PRIMARY_START).grid(row=0, column=1, sticky="nsew", padx=12)
    kpi_card(kpi_row, "Empleados Activos", "28", "91.0% del plantel", SUCCESS).grid(row=0, column=2, sticky="nsew", padx=12)
    kpi_card(kpi_row, "Productos con Bajo Stock", "12", "4 críticos", "#695123").grid(row=0, column=3, sticky="nsew", padx=(12, 0))

    middle = ctk.CTkFrame(content, fg_color="transparent")
    middle.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))
    middle.grid_columnconfigure(0, weight=2)
    middle.grid_columnconfigure(1, weight=1)

    chart_panel = ctk.CTkFrame(middle, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E3E4E0")
    chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    chart_panel.grid_columnconfigure(0, weight=1)
    chart_panel.grid_rowconfigure(0, weight=1)
    ctk.CTkLabel(chart_panel, text="Tendencia de ventas semanales", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
    canvas = tk.Canvas(chart_panel, width=600, height=220, bg=PANEL, highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    # Grid lines
    for y in range(20, 220, 30):
        canvas.create_line(26, y, 575, y, fill="#D3D5D2", width=1)
    for x in range(60, 560, 60):
        canvas.create_line(x, 20, x, 200, fill="#D3D5D2", width=1)
    data = [110, 150, 130, 180, 160, 210, 200]
    xs = [36 + i * 75 for i in range(len(data))]
    ys = [190 - v for v in data]
    poly = [(x, y) for x, y in zip(xs, ys)]
    canvas.create_line(*sum(([x, y] for x, y in poly), []), fill="#3A5771", width=4, smooth=True)
    for x, y in poly:
        canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#2D4F6A", outline="#2D4F6A")

    ranking = ctk.CTkFrame(middle, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E3E4E0")
    ranking.grid(row=0, column=1, sticky="nsew")
    ctk.CTkLabel(ranking, text="Top productos", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
    product_rows = [
        ("1", "Café Premium", "198 unidades"),
        ("2", "Galletas Clásicas", "176 unidades"),
        ("3", "Jugo Natural", "154 unidades"),
        ("4", "Pan Integral", "120 unidades"),
        ("5", "Yogur Frutal", "103 unidades"),
    ]
    for idx, (n, name, qty) in enumerate(product_rows, start=1):
        row = ctk.CTkFrame(ranking, fg_color="transparent")
        row.grid(row=idx, column=0, sticky="ew", padx=16, pady=4)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=n, text_color=PRIMARY_START, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 14))
        ctk.CTkLabel(row, text=name, text_color=TEXT, font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(row, text=qty, text_color="#5B5B5B", font=ctk.CTkFont(size=10)).grid(row=0, column=2, sticky="e")



def employee_screen(parent):
    frame = ctk.CTkFrame(parent, fg_color=BG, corner_radius=24)
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    create_sidebar(frame, "Juan Pérez", "Empleado", "Caja")

    content = ctk.CTkFrame(frame, fg_color=BG, corner_radius=18)
    content.grid(row=0, column=1, sticky="nsew", padx=(16, 14), pady=14)
    content.grid_columnconfigure(0, weight=1)

    topbar = ctk.CTkFrame(content, fg_color="transparent")
    topbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 8))
    topbar.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(topbar, text="Turno Activo", text_color=TEXT, font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
    badge = ctk.CTkFrame(topbar, fg_color="#E8F5EE", corner_radius=12)
    badge.grid(row=0, column=1, sticky="e")
    ctk.CTkLabel(badge, text="En Línea • 08:00 - 17:00", text_color=SUCCESS_DARK, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=14, pady=8)

    kpi_row = ctk.CTkFrame(content, fg_color="transparent")
    kpi_row.grid(row=1, column=0, sticky="ew", padx=10, pady=6)
    kpi_row.grid_columnconfigure((0, 1, 2), weight=1)
    kpi_card(kpi_row, "Ventas del Turno", "S/. 2,640", "+12 ventas", PRIMARY_START).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    kpi_card(kpi_row, "Transacciones", "41", "+5 hoy", PRIMARY_START).grid(row=0, column=1, sticky="nsew", padx=12)
    kpi_card(kpi_row, "Horas en Turno", "7h 40m", "Operativo", SUCCESS).grid(row=0, column=2, sticky="nsew", padx=(12, 0))

    middle = ctk.CTkFrame(content, fg_color="transparent")
    middle.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))
    middle.grid_columnconfigure(0, weight=2)
    middle.grid_columnconfigure(1, weight=1)

    catalog = ctk.CTkFrame(middle, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E3E4E0")
    catalog.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    catalog.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(catalog, text="Buscar Producto", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))
    search = ctk.CTkEntry(catalog, height=40, placeholder_text="Código o nombre del producto", corner_radius=10, fg_color="#F9F9F7")
    search.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

    product_table = ttk.Treeview(catalog, columns=("cod", "nombre", "precio", "stock"), show="headings", height=10)
    product_table.heading("cod", text="Código")
    product_table.heading("nombre", text="Producto")
    product_table.heading("precio", text="Precio")
    product_table.heading("stock", text="Stock")
    product_table.column("cod", width=90, anchor="center")
    product_table.column("nombre", width=220, anchor="w")
    product_table.column("precio", width=90, anchor="center")
    product_table.column("stock", width=80, anchor="center")
    product_table.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
    for row in [
        ("001", "Café Americano", "S/. 8.50", "34"),
        ("021", "Sandwich de Pollo", "S/. 18.00", "16"),
        ("034", "Jugo Natural", "S/. 11.00", "22"),
        ("055", "Pan con Mantequilla", "S/. 9.00", "27"),
        ("072", "Galletas Clásicas", "S/. 7.50", "31"),
    ]:
        product_table.insert("", "end", values=row)

    cart = ctk.CTkFrame(middle, fg_color=PANEL, corner_radius=18, border_width=1, border_color="#E3E4E0")
    cart.grid(row=0, column=1, sticky="nsew")
    cart.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(cart, text="Carrito Actual", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

    cart_table = ttk.Treeview(cart, columns=("prod", "cant", "precio", "subtotal"), show="headings", height=6)
    cart_table.heading("prod", text="Producto")
    cart_table.heading("cant", text="Cant.")
    cart_table.heading("precio", text="P.U.")
    cart_table.heading("subtotal", text="Total")
    cart_table.column("prod", width=140, anchor="w")
    cart_table.column("cant", width=60, anchor="center")
    cart_table.column("precio", width=70, anchor="center")
    cart_table.column("subtotal", width=80, anchor="center")
    cart_table.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))
    for row in [
        ("Café Americano", "2", "S/. 8.50", "S/. 17.00"),
        ("Sandwich", "1", "S/. 18.00", "S/. 18.00"),
        ("Jugo Natural", "1", "S/. 11.00", "S/. 11.00"),
    ]:
        cart_table.insert("", "end", values=row)

    totals = ctk.CTkFrame(cart, fg_color="transparent")
    totals.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
    totals.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(totals, text="Subtotal", text_color="#5D5D5D", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(totals, text="S/. 46.00", text_color=TEXT, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="e")
    ctk.CTkLabel(totals, text="Total", text_color=TEXT, font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
    ctk.CTkLabel(totals, text="S/. 46.00", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=1, sticky="e", pady=(8, 0))

    ctk.CTkButton(cart, text="Cobrar Venta", height=42, corner_radius=12, fg_color=SUCCESS, hover_color="#419165", text_color=TEXT_LIGHT, font=ctk.CTkFont(size=15, weight="bold")).grid(row=3, column=0, sticky="ew", padx=16, pady=(10, 16))


class UIConceptApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Unilink POS — UI Concept")
        self.geometry("1920x1080")
        self.minsize(1500, 900)
        self.configure(fg_color=BG)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        admin_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=24, width=620, height=960)
        admin_frame.grid(row=0, column=0, sticky="nsew", padx=(14, 8), pady=14)
        admin_frame.grid_propagate(False)
        admin_screen(admin_frame)

        employer_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=24, width=620, height=960)
        employer_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=14)
        employer_frame.grid_propagate(False)
        employer_screen(employer_frame)

        employee_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=24, width=620, height=960)
        employee_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 14), pady=14)
        employee_frame.grid_propagate(False)
        employee_screen(employee_frame)


if __name__ == "__main__":
    set_theme()
    app = UIConceptApp()
    app.mainloop()
