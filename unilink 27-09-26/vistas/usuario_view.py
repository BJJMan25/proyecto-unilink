import customtkinter as ctk
from tkinter import ttk, messagebox
from modelo.usuario import Usuario

class UsuariosView(ctk.CTkFrame):
    def __init__(self, master, usuario_controller):
        super().__init__(master, fg_color="transparent")

        self.usuario_controller = usuario_controller
        self.roles = self.usuario_controller.obtener_roles()

        self._crear_header()
        self._crear_tabla()
        self._cargar_usuarios()

    def _crear_header(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        # Ahora solo se muestra el título de la sección
        ctk.CTkLabel(
            header, text="Gestión de Usuarios",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="+ Registrar Usuario", width=170, height=34,
            command=self._abrir_formulario_registro
        ).grid(row=0, column=1, sticky="e")

    def _crear_tabla(self):
        try:
            from ..assets.styles.estilos import estilizar_tabla
            estilizar_tabla()
        except (ModuleNotFoundError, ImportError):
            try:
                from ..recursos.styles.estilos import estilizar_tabla
                estilizar_tabla()
            except (ModuleNotFoundError, ImportError):
                print("[ADVERTENCIA] No se encontró el módulo de estilos en la raíz. Usando Treeview estándar.")

        self.bind("<Configure>", self._ajustar_botones_usuarios)
        self.grid_rowconfigure(1, weight=1)

        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 12))
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "nombre_completo", "usuario", "rol", "estado", "fecha")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=12)

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre_completo", text="Nombre Completo", anchor="w")
        self.tree.heading("usuario", text="Usuario", anchor="w")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("fecha", text="Fecha Creación")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre_completo", width=200)
        self.tree.column("usuario", width=180)
        self.tree.column("rol", width=140, anchor="center")
        self.tree.column("estado", width=100, anchor="center")
        self.tree.column("fecha", width=180, anchor="center")

        scroll = ctk.CTkScrollbar(tabla_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=8)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 18))
        self.btn_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.btn_activar = ctk.CTkButton(
            self.btn_frame, text="Activar", width=120, height=34,
            fg_color="#2FA572", hover_color="#288F62",
            command=lambda: self._cambiar_estado(1)
        )
        self.btn_editar = ctk.CTkButton(
            self.btn_frame, text="Editar", width=120, height=34,
            command=self._abrir_formulario_edicion
        )
        self.btn_contrasena = ctk.CTkButton(
            self.btn_frame, text="Editar Contraseña", width=150, height=34,
            command=self._abrir_formulario_contrasena
        )
        self.btn_desactivar = ctk.CTkButton(
            self.btn_frame, text="Desactivar", width=120, height=34,
            fg_color="#C0392B", hover_color="#A93226",
            command=lambda: self._cambiar_estado(0)
        )
        self.btn_refrescar = ctk.CTkButton(
            self.btn_frame, text="Refrescar", width=120, height=34,
            fg_color="gray", hover_color="gray30",
            command=self._cargar_usuarios
        )

        self.after(50, self._ajustar_botones_usuarios)

    def _ajustar_botones_usuarios(self, event=None):
        if not hasattr(self, "btn_frame") or self.btn_frame is None:
            return

        for child in self.btn_frame.winfo_children():
            child.grid_forget()

        ancho = max(self.winfo_width(), 1)
        botones = list(self.btn_frame.winfo_children())
        if ancho < 1000:
            for idx, btn in enumerate(botones):
                fila = idx // 2
                col = idx % 2
                btn.grid(row=fila, column=col, padx=(0, 6), pady=4, sticky="ew")
            self.btn_frame.grid_columnconfigure((0, 1), weight=1)
        else:
            for idx, btn in enumerate(botones):
                btn.grid(row=0, column=idx, padx=(0, 6), pady=0, sticky="ew")
            self.btn_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    def _obtener_usuario_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return None

        usuario_id = self.tree.item(sel[0])["values"][0]
        usuario = self.usuario_controller.obtener_usuario_por_id(usuario_id)
        if not usuario:
            messagebox.showerror("Error", "No se pudo obtener el usuario seleccionado")
            return None
        return usuario

    def _cambiar_estado(self, estado):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return

        usuario_id = self.tree.item(sel[0])["values"][0]
        exito, mensaje = self.usuario_controller.cambiar_estado_usuario(usuario_id, estado)
        if exito:
            self._cargar_usuarios()
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    def _abrir_formulario_registro(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registrar Usuario")
        dialogo.geometry("430x560")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.grid_columnconfigure(0, weight=1)

        row_idx = 0
        ctk.CTkLabel(
            dialogo, text="Registrar Nuevo Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row_idx, column=0, pady=(25, 18))
        row_idx += 1

        entry_nombre = ctk.CTkEntry(dialogo, placeholder_text="Nombre completo", width=320, height=36)
        entry_nombre.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_usuario = ctk.CTkEntry(dialogo, placeholder_text="Nombre de usuario", width=320, height=36)
        entry_usuario.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_contrasena = ctk.CTkEntry(dialogo, placeholder_text="Contraseña", show="●", width=320, height=36)
        entry_contrasena.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_confirmar = ctk.CTkEntry(dialogo, placeholder_text="Confirmar contraseña", show="●", width=320, height=36)
        entry_confirmar.grid(row=row_idx, column=0, pady=(0, 12))
        row_idx += 1

        ctk.CTkLabel(dialogo, text="Rol", anchor="w").grid(row=row_idx, column=0, sticky="w", padx=55, pady=(0, 6))
        row_idx += 1

        roles_texto = [f"{rol[0]} - {rol[1]}" for rol in self.roles]
        combo_roles = ctk.CTkComboBox(dialogo, values=roles_texto, width=320, height=36, state="readonly")
        combo_roles.grid(row=row_idx, column=0, pady=(0, 18))
        if roles_texto:
            combo_roles.set(roles_texto[0])
        row_idx += 1

        lbl_estado = ctk.CTkLabel(dialogo, text="Complete los campos para habilitar el registro", text_color="gray")
        lbl_estado.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        def validar_formulario():
            nombre_completo = entry_nombre.get().strip()
            nombre_usuario = entry_usuario.get().strip()
            contrasena = entry_contrasena.get().strip()
            confirmar = entry_confirmar.get().strip()

            if not roles_texto:
                lbl_estado.configure(text="No hay roles disponibles para registrar", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            if not nombre_completo or not nombre_usuario or not contrasena or not confirmar:
                lbl_estado.configure(text="Todos los campos son obligatorios", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            if len(nombre_completo) < 3:
                lbl_estado.configure(text="Nombre completo: minimo 3 caracteres", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            if len(nombre_usuario) < 3:
                lbl_estado.configure(text="Usuario: minimo 3 caracteres", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            if len(contrasena) < 4:
                lbl_estado.configure(text="Contrasena: minimo 4 caracteres", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            if contrasena != confirmar:
                lbl_estado.configure(text="Las contrasenas no coinciden", text_color="#C0392B")
                btn_registrar.configure(state="disabled")
                return False

            lbl_estado.configure(text="Formulario valido", text_color="#2FA572")
            btn_registrar.configure(state="normal")
            return True

        def registrar():
            if not validar_formulario():
                return

            nombre_completo = entry_nombre.get().strip()
            nombre_usuario = entry_usuario.get().strip()
            contrasena = entry_contrasena.get().strip()
            confirmar = entry_confirmar.get().strip()
            rol_seleccionado = combo_roles.get().strip()

            if not rol_seleccionado:
                messagebox.showerror("Error", "Seleccione un rol")
                return

            rol_id = int(rol_seleccionado.split(" - ")[0])

            usuario = Usuario(
                nombre_completo=nombre_completo,
                nombre_usuario=nombre_usuario,
                contrasena=contrasena,
                rol_id=rol_id,
                activo=1
            )

            exito, mensaje = self.usuario_controller.registrar_usuario(usuario, confirmar)
            if exito:
                self._cargar_usuarios()
                messagebox.showinfo("Éxito", mensaje)
                dialogo.destroy()
            else:
                messagebox.showerror("Error", mensaje)

        btn_registrar = ctk.CTkButton(
            dialogo, text="Registrar", width=320, height=38,
            command=registrar
        )
        btn_registrar.grid(row=row_idx, column=0)

        entry_nombre.bind("<KeyRelease>", lambda _e: validar_formulario())
        entry_usuario.bind("<KeyRelease>", lambda _e: validar_formulario())
        entry_contrasena.bind("<KeyRelease>", lambda _e: validar_formulario())
        entry_confirmar.bind("<KeyRelease>", lambda _e: validar_formulario())
        combo_roles.bind("<<ComboboxSelected>>", lambda _e: validar_formulario())
        validar_formulario()

    def _abrir_formulario_edicion(self):
        usuario = self._obtener_usuario_seleccionado()
        if not usuario:
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Editar Usuario")
        dialogo.geometry("430x500")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.grid_columnconfigure(0, weight=1)

        row_idx = 0
        ctk.CTkLabel(
            dialogo, text="Editar Usuario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row_idx, column=0, pady=(25, 18))
        row_idx += 1

        entry_nombre = ctk.CTkEntry(dialogo, width=320, height=36)
        entry_nombre.insert(0, usuario.nombre_completo)
        entry_nombre.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_usuario = ctk.CTkEntry(dialogo, width=320, height=36)
        entry_usuario.insert(0, usuario.nombre_usuario)
        entry_usuario.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        ctk.CTkLabel(dialogo, text="Rol", anchor="w").grid(row=row_idx, column=0, sticky="w", padx=55, pady=(0, 6))
        row_idx += 1

        roles_texto = [f"{rol[0]} - {rol[1]}" for rol in self.roles]
        combo_roles = ctk.CTkComboBox(dialogo, values=roles_texto, width=320, height=36, state="readonly")
        combo_roles.grid(row=row_idx, column=0, pady=(0, 18))
        rol_actual = next((r for r in roles_texto if r.startswith(f"{usuario.rol_id} - ")), "")
        if rol_actual:
            combo_roles.set(rol_actual)
        elif roles_texto:
            combo_roles.set(roles_texto[0])
        row_idx += 1

        lbl_estado = ctk.CTkLabel(dialogo, text="Edite los datos del usuario", text_color="gray")
        lbl_estado.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        def validar_edicion():
            nombre_completo = entry_nombre.get().strip()
            nombre_usuario = entry_usuario.get().strip()
            rol_seleccionado = combo_roles.get().strip()

            if not roles_texto:
                lbl_estado.configure(text="No hay roles disponibles", text_color="#C0392B")
                btn_guardar.configure(state="disabled")
                return False

            if not nombre_completo or not nombre_usuario or not rol_seleccionado:
                lbl_estado.configure(text="Todos los campos son obligatorios", text_color="#C0392B")
                btn_guardar.configure(state="disabled")
                return False

            if len(nombre_completo) < 3:
                lbl_estado.configure(text="Nombre completo: minimo 3 caracteres", text_color="#C0392B")
                btn_guardar.configure(state="disabled")
                return False

            if len(nombre_usuario) < 3:
                lbl_estado.configure(text="Usuario: minimo 3 caracteres", text_color="#C0392B")
                btn_guardar.configure(state="disabled")
                return False

            lbl_estado.configure(text="Datos validos", text_color="#2FA572")
            btn_guardar.configure(state="normal")
            return True

        def guardar_edicion():
            if not validar_edicion():
                return

            rol_id = int(combo_roles.get().split(" - ")[0])
            usuario_editado = Usuario(
                id=usuario.id,
                nombre_completo=entry_nombre.get().strip(),
                nombre_usuario=entry_usuario.get().strip(),
                rol_id=rol_id
            )

            exito, mensaje = self.usuario_controller.editar_usuario(usuario_editado)
            if exito:
                self._cargar_usuarios()
                messagebox.showinfo("Éxito", mensaje)
                dialogo.destroy()
            else:
                messagebox.showerror("Error", mensaje)

        btn_guardar = ctk.CTkButton(
            dialogo, text="Guardar Cambios", width=320, height=38,
            command=guardar_edicion
        )
        btn_guardar.grid(row=row_idx, column=0)

        entry_nombre.bind("<KeyRelease>", lambda _e: validar_edicion())
        entry_usuario.bind("<KeyRelease>", lambda _e: validar_edicion())
        combo_roles.bind("<<ComboboxSelected>>", lambda _e: validar_edicion())
        validar_edicion()

    def _abrir_formulario_contrasena(self):
        usuario = self._obtener_usuario_seleccionado()
        if not usuario:
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Editar Contraseña")
        dialogo.geometry("430x360")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.grid_columnconfigure(0, weight=1)

        row_idx = 0
        ctk.CTkLabel(
            dialogo, text=f"Cambiar contraseña de: {usuario.nombre_usuario}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row_idx, column=0, pady=(25, 18))
        row_idx += 1

        entry_nueva = ctk.CTkEntry(dialogo, placeholder_text="Nueva contraseña", show="●", width=320, height=36)
        entry_nueva.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_confirmar = ctk.CTkEntry(dialogo, placeholder_text="Confirmar nueva contraseña", show="●", width=320, height=36)
        entry_confirmar.grid(row=row_idx, column=0, pady=(0, 18))
        row_idx += 1

        lbl_estado = ctk.CTkLabel(dialogo, text="Ingrese la nueva contraseña", text_color="gray")
        lbl_estado.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        def validar_contrasena():
            nueva = entry_nueva.get().strip()
            confirmar = entry_confirmar.get().strip()

            if not nueva or not confirmar:
                lbl_estado.configure(text="Complete ambos campos", text_color="#C0392B")
                btn_actualizar.configure(state="disabled")
                return False

            if len(nueva) < 4:
                lbl_estado.configure(text="Contrasena: minimo 4 caracteres", text_color="#C0392B")
                btn_actualizar.configure(state="disabled")
                return False

            if nueva != confirmar:
                lbl_estado.configure(text="Las contrasenas no coinciden", text_color="#C0392B")
                btn_actualizar.configure(state="disabled")
                return False

            lbl_estado.configure(text="Contrasena valida", text_color="#2FA572")
            btn_actualizar.configure(state="normal")
            return True

        def actualizar_contrasena():
            if not validar_contrasena():
                return

            exito, mensaje = self.usuario_controller.editar_contrasena_usuario(
                usuario.id,
                entry_nueva.get().strip(),
                entry_confirmar.get().strip()
            )
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                dialogo.destroy()
            else:
                messagebox.showerror("Error", mensaje)

        btn_actualizar = ctk.CTkButton(
            dialogo, text="Actualizar Contraseña", width=320, height=38,
            command=actualizar_contrasena
        )
        btn_actualizar.grid(row=row_idx, column=0)

        entry_nueva.bind("<KeyRelease>", lambda _e: validar_contrasena())
        entry_confirmar.bind("<KeyRelease>", lambda _e: validar_contrasena())
        validar_contrasena()

    def _cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = self.usuario_controller.obtener_usuarios()
        for u in usuarios:
            estado = "Activo" if u.activo == 1 else "Inactivo"
            self.tree.insert("", "end", values=(u.id, u.nombre_completo, u.nombre_usuario, u.rol_nombre, estado, u.fecha_creacion))