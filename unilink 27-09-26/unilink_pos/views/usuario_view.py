import customtkinter as ctk


class UsuarioView(ctk.CTkFrame):
    """Vista de gestión de usuarios."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_layout()

    def _build_layout(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(container, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Gestión de usuarios",
            text_color="#111827",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        ctk.CTkLabel(
            header,
            text="Administra accesos, perfiles y actividad del personal.",
            text_color="#64748B",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 18))

        toolbar = ctk.CTkFrame(container, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        toolbar.grid_columnconfigure(0, weight=1)
        toolbar.grid_columnconfigure(1, weight=0)

        ctk.CTkEntry(toolbar, placeholder_text="Buscar usuario", width=300, height=38).grid(row=0, column=0, sticky="w", padx=(0, 12))
        ctk.CTkButton(
            toolbar,
            text="Nuevo usuario",
            fg_color="#2FA572",
            hover_color="#237D58",
            width=150,
            height=38,
        ).grid(row=0, column=1, sticky="e")

        table = ctk.CTkFrame(container, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        table.grid(row=2, column=0, sticky="ew")
        table.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Nombre", "Rol", "Estado", "Último acceso", "Acciones"]
        for index, header in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=header,
                text_color="#475569",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=index, sticky="w", padx=12, pady=(16, 10))

        rows = [
            ("Ana García", "Administrador", "Activo", "18:40", "Editar / Restablecer"),
            ("Luis Pérez", "Cajero", "Activo", "17:20", "Editar / Restablecer"),
            ("María Suárez", "Supervisor", "Inactivo", "Lunes", "Editar / Activar"),
        ]

        for row_idx, row in enumerate(rows, start=1):
            for col_idx, value in enumerate(row):
                ctk.CTkLabel(
                    table,
                    text=str(value),
                    text_color="#111827",
                    font=ctk.CTkFont(size=11),
                ).grid(row=row_idx, column=col_idx, sticky="w", padx=12, pady=12)

        ctk.CTkButton(
            table,
            text="Guardar cambios",
            fg_color="#2FA572",
            hover_color="#237D58",
            width=180,
            height=40,
        ).grid(row=len(rows) + 1, column=4, sticky="e", padx=12, pady=(10, 18))
