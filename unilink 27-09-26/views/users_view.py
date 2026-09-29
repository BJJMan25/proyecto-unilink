import customtkinter as ctk
from tkinter import ttk, messagebox

from database import MySQLConnection


class UsersView(ctk.CTkFrame):
    """Vista de gestión de usuarios y administración del sistema."""

    ROLE_OPTIONS = ["Administrador", "Empleador", "Empleado"]

    def __init__(self, parent, db=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.db = db or MySQLConnection()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self._build_toolbar()
        self.refresh_users()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Gestión de Usuarios",
            text_color="#111827",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Registrar usuario",
            width=170,
            height=38,
            corner_radius=12,
            fg_color="#2FA572",
            hover_color="#248963",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_register_modal
        ).grid(row=0, column=1, sticky="e")

    def _build_table(self):
        table_container = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#E7ECEF", corner_radius=18)
        table_container.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 12))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        cols = ("id", "nombre_completo", "usuario", "rol", "estado", "fecha_creacion")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", height=12)

        headers = {
            "id": "ID",
            "nombre_completo": "Nombre Completo",
            "usuario": "Usuario",
            "rol": "Rol",
            "estado": "Estado",
            "fecha_creacion": "Fecha de Creación",
        }
        for key, label in headers.items():
            self.tree.heading(key, text=label)

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("nombre_completo", width=220, anchor="w")
        self.tree.column("usuario", width=170, anchor="w")
        self.tree.column("rol", width=170, anchor="center")
        self.tree.column("estado", width=120, anchor="center")
        self.tree.column("fecha_creacion", width=170, anchor="center")

        scroll_y = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 20))
        toolbar.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        actions = [
            ("Activar", "#2FA572", lambda: self._set_user_status(1)),
            ("Desactivar", "#E11D48", lambda: self._set_user_status(0)),
            ("Editar", "#1F2937", self._open_edit_modal),
            ("Cambiar Contraseña", "#2563EB", self._open_password_modal),
            ("Refrescar", "#64748B", self.refresh_users),
        ]

        for idx, (label, color, command) in enumerate(actions):
            btn = ctk.CTkButton(
                toolbar,
                text=label,
                height=38,
                corner_radius=10,
                fg_color=color,
                hover_color="#1F2B2F" if color == "#1F2937" else "#1A2430",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=command,
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 8, 0))

    def refresh_users(self):
        self.tree.delete(*self.tree.get_children())

        try:
            rows = self.db.fetch_all(
                """
                SELECT u.id_usuario, u.nombre, u.usuario, r.nombre AS rol, u.estado,
                       DATE_FORMAT(u.fecha_creacion, '%Y-%m-%d') AS fecha_creacion
                FROM usuarios u
                LEFT JOIN roles r ON r.id_rol = u.id_rol
                ORDER BY u.id_usuario ASC
                """
            )
            for row in rows or []:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["id_usuario"],
                        row["nombre"],
                        row["usuario"],
                        row["rol"] or "Sin rol",
                        "Activo" if row["estado"] == 1 or row["estado"] == "1" else "Inactivo",
                        row["fecha_creacion"] or "-",
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Error de datos", f"No se pudieron cargar los usuarios: {exc}")

    def _get_selected_user(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Selecciona un usuario antes de continuar.")
            return None

        user_id = self.tree.item(selection[0], "values")[0]
        row = self.db.fetch_one(
            """
            SELECT u.id_usuario, u.nombre, u.usuario, u.id_rol, r.nombre AS rol, u.estado
            FROM usuarios u
            LEFT JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s
            """,
            (user_id,),
        )
        return row

    def _set_user_status(self, state):
        row = self._get_selected_user()
        if row is None:
            return

        try:
            self.db.execute(
                "UPDATE usuarios SET estado = %s WHERE id_usuario = %s",
                (int(state), row["id_usuario"]),
            )
            self.db.log_action(
                "Cambio de estado",
                f"Usuario {row['usuario']} actualizado a {'activo' if state else 'inactivo'}",
                user_id=row["id_usuario"],
            )
            messagebox.showinfo("Éxito", "Estado actualizado correctamente.")
            self.refresh_users()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {exc}")

    def _open_register_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Registrar Nuevo Usuario")
        modal.geometry("860x520")
        modal.minsize(760, 460)
        modal.grab_set()
        modal.transient(self)
        modal.configure(fg_color="#F4F6F8")

        main = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=18)
        main.pack(fill="both", expand=True, padx=18, pady=18)
        main.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(main, text="Registrar Nuevo Usuario", text_color="#111827", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 12))

        left = ctk.CTkFrame(main, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0", corner_radius=16)
        left.grid(row=1, column=0, padx=(18, 10), pady=(0, 18), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(main, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0", corner_radius=16)
        right.grid(row=1, column=1, padx=(10, 18), pady=(0, 18), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Datos Personales", text_color="#111827", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        nombre = ctk.CTkEntry(left, placeholder_text="Nombre completo", height=38)
        nombre.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        usuario = ctk.CTkEntry(left, placeholder_text="Usuario", height=38)
        usuario.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        rol_var = ctk.StringVar(value=self.ROLE_OPTIONS[0])
        ctk.CTkLabel(left, text="Rol", text_color="#374151", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, sticky="w", padx=16, pady=(10, 6))
        rol_combo = ctk.CTkOptionMenu(left, values=self.ROLE_OPTIONS, variable=rol_var, width=250, height=36)
        rol_combo.grid(row=4, column=0, padx=16, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(right, text="Seguridad y Login", text_color="#111827", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        password = ctk.CTkEntry(right, placeholder_text="Contraseña", show="●", height=38)
        password.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        confirm = ctk.CTkEntry(right, placeholder_text="Confirmar contraseña", show="●", height=38)
        confirm.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        status = ctk.CTkLabel(right, text="Completa los datos para continuar", text_color="#64748B", font=ctk.CTkFont(size=12))
        status.grid(row=3, column=0, padx=16, pady=(12, 8), sticky="w")

        def validate():
            valid = bool(nombre.get().strip()) and bool(usuario.get().strip()) and bool(password.get().strip()) and bool(confirm.get().strip())
            if not valid:
                status.configure(text="Completa los campos obligatorios", text_color="#E11D48")
                return False
            if password.get().strip() != confirm.get().strip():
                status.configure(text="Las contraseñas no coinciden", text_color="#E11D48")
                return False
            if len(password.get().strip()) < 4:
                status.configure(text="La contraseña debe tener al menos 4 caracteres", text_color="#E11D48")
                return False
            status.configure(text="Formulario válido", text_color="#2FA572")
            return True

        def save_user():
            if not validate():
                return

            role_name = rol_var.get()
            try:
                self.db.create_user(
                    nombre=nombre.get().strip(),
                    username=usuario.get().strip(),
                    password=password.get().strip(),
                    role_name=role_name,
                )
                messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
                self.refresh_users()
                modal.destroy()
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo guardar el usuario: {exc}")

        actions = ctk.CTkFrame(main, fg_color="transparent")
        actions.grid(row=2, column=0, columnspan=2, sticky="e", padx=18, pady=(0, 18))

        ctk.CTkButton(actions, text="Cancelar", width=120, height=38, fg_color="#64748B", hover_color="#475569", command=modal.destroy).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(actions, text="Guardar", width=160, height=38, fg_color="#2FA572", hover_color="#248963", command=save_user).grid(row=0, column=1)

        nombre.bind("<KeyRelease>", lambda event: validate())
        usuario.bind("<KeyRelease>", lambda event: validate())
        password.bind("<KeyRelease>", lambda event: validate())
        confirm.bind("<KeyRelease>", lambda event: validate())

    def _open_edit_modal(self):
        row = self._get_selected_user()
        if row is None:
            return
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Usuario")
        modal.geometry("500x420")
        modal.grab_set()
        modal.transient(self)

        ctk.CTkLabel(modal, text="Editar Usuario", text_color="#111827", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=18, pady=(18, 12))

        form = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=18)
        form.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        form.grid_columnconfigure(0, weight=1)

        name_entry = ctk.CTkEntry(form, placeholder_text="Nombre completo", height=38)
        name_entry.insert(0, row["nombre"])
        name_entry.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")

        user_entry = ctk.CTkEntry(form, placeholder_text="Usuario", height=38)
        user_entry.insert(0, row["usuario"])
        user_entry.grid(row=1, column=0, padx=18, pady=6, sticky="ew")

        role_var = ctk.StringVar(value=row["rol"] or "Empleado")
        role_menu = ctk.CTkOptionMenu(form, values=self.ROLE_OPTIONS, variable=role_var, width=300, height=36)
        role_menu.grid(row=2, column=0, padx=18, pady=10, sticky="ew")

        def save():
            try:
                self.db.execute(
                    "UPDATE usuarios SET nombre = %s, usuario = %s, id_rol = %s WHERE id_usuario = %s",
                    (
                        name_entry.get().strip(),
                        user_entry.get().strip(),
                        self.db.ROLE_MAP.get(role_var.get(), 3),
                        row["id_usuario"],
                    ),
                )
                self.db.log_action("Edición de usuario", f"Se editó el usuario {user_entry.get().strip()}", user_id=row["id_usuario"])
                messagebox.showinfo("Éxito", "Usuario editado correctamente.")
                modal.destroy()
                self.refresh_users()
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo editar el usuario: {exc}")

        ctk.CTkButton(form, text="Guardar cambios", width=220, height=38, fg_color="#2FA572", hover_color="#248963", command=save).grid(row=3, column=0, padx=18, pady=(16, 18))

    def _open_password_modal(self):
        row = self._get_selected_user()
        if row is None:
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Cambiar Contraseña")
        modal.geometry("420x280")
        modal.grab_set()
        modal.transient(self)

        ctk.CTkLabel(modal, text=f"Usuario: {row['usuario']}", text_color="#111827", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))

        password = ctk.CTkEntry(modal, placeholder_text="Nueva contraseña", show="●", width=300, height=38)
        password.pack(padx=20, pady=(0, 10))

        confirm = ctk.CTkEntry(modal, placeholder_text="Confirmar contraseña", show="●", width=300, height=38)
        confirm.pack(padx=20, pady=(0, 16))

        def save_password():
            if password.get().strip() != confirm.get().strip():
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return
            if len(password.get().strip()) < 4:
                messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
                return

            try:
                self.db.execute(
                    "UPDATE usuarios SET password = %s WHERE id_usuario = %s",
                    (self.db.hash_password(password.get().strip()), row["id_usuario"]),
                )
                self.db.log_action("Cambio de contraseña", f"Contraseña actualizada para {row['usuario']}", user_id=row["id_usuario"])
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
                modal.destroy()
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo cambiar la contraseña: {exc}")

        ctk.CTkButton(modal, text="Guardar contraseña", width=200, height=38, fg_color="#2FA572", hover_color="#248963", command=save_password).pack(pady=(0, 20))


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1200x760")
    UsersView(root).pack(fill="both", expand=True)
    root.mainloop()
