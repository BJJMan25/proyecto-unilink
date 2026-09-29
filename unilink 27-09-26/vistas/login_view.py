
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from config import ICON_PATH, IMAGE_POST
from controladores.usuario_controller import UsuarioController

class LoginView(ctk.CTk):

    # CORRECCIÓN: Ahora acepta el controlador único que viene desde main.py
    def __init__(self, usuario_controller):
        super().__init__()

        self.title("Punto de Venta - Login")
        self.geometry("900x650")
        self.minsize(480, 520)
        self.resizable(True, True)

        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        # Asignamos el controlador inyectado
        self.usuario_controller = usuario_controller
        self.card = None

        self._crear_widgets()
        self.bind("<Configure>", self._ajustar_card)

    def _crear_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.card = ctk.CTkFrame(self, corner_radius=24)
        self.card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)

        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(IMAGE_POST),
                dark_image=Image.open(IMAGE_POST),
                size=(150, 150))
            logo_label = ctk.CTkLabel(self.card, image=logo_image, text="")
            logo_label.grid(row=0, column=0, pady=(20, 0))
        except Exception:
            pass

        # Títulos
        ctk.CTkLabel(
            self.card, text="Punto de Venta",
            font=ctk.CTkFont(size=30, weight="bold")
        ).grid(row=1, column=0, pady=(35, 5))

        ctk.CTkLabel(
            self.card,
            text="Inicie sesión para continuar en el sistema de Punto de Venta.",
            font=ctk.CTkFont(size=14, weight="normal")
        ).grid(row=2, column=0, pady=(0, 30), padx=20)

        # Campo de entrada: Usuario
        self.entry_usuario = ctk.CTkEntry(
            self.card, placeholder_text="Nombre de Usuario", width=300, height=40,
            font=ctk.CTkFont(size=16, weight="normal")
        )
        self.entry_usuario.grid(row=3, column=0, pady=(0, 12), sticky="ew", padx=26)

        # Al presionar Enter, pasar al campo de contraseña
        self.entry_usuario.bind("<Return>", lambda e: self.entry_contrasena.focus())

        # Campo de entrada: Contraseña
        self.entry_contrasena = ctk.CTkEntry(
            self.card, placeholder_text="Contraseña", show="●", width=300, height=40,
            font=ctk.CTkFont(size=16, weight="normal")
        )
        self.entry_contrasena.grid(row=4, column=0, pady=(0, 12), sticky="ew", padx=26)

        # Al presionar Enter, ejecutar el login
        self.entry_contrasena.bind("<Return>", lambda e: self._login())

        # Botón de Inicio de Sesión
        ctk.CTkButton(
            self.card, text="Iniciar Sesión", width=300, height=38,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._login
        ).grid(row=5, column=0, pady=(0, 15), sticky="ew", padx=26)

    def _ajustar_card(self, event=None):
        if self.card is None:
            return
        ancho = max(320, min(560, self.winfo_width() - 80))
        self.card.configure(width=ancho)

    def _login(self):
        nombre_usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not nombre_usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Por favor, llene todos los campos.")
            return

        exito, mensaje = self.usuario_controller.login(nombre_usuario, contrasena)

        if exito:
            # Indicamos a la ventana que se cierre limpiamente y rompa SU propio mainloop
            self.quit() 
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)