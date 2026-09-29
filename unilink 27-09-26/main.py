import customtkinter as ctk
from controladores.usuario_controller import UsuarioController
from services.currency_service import CurrencyService
from vistas.login_view import LoginView
from vistas.main_view import MainView


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    currency_service = CurrencyService()
    currency_service.start_background_sync(interval_hours=6)

    usuario_controller = UsuarioController()

    print("[1] Iniciando ventana de Autenticación...")
    login_app = LoginView(usuario_controller)
    login_app.mainloop()

    if usuario_controller.usuario_actual is not None:
        print("[2] Login exitoso. Inicializando Panel Principal (MainView)...")
        main_app = MainView(usuario_controller)
        main_app.mainloop()
        print("[3] Sistema cerrado de manera segura por el operador.")
    else:
        print("[INFO] Ventana de inicio de sesión cerrada sin autenticar. Finalizando aplicación.")

    currency_service.stop_background_sync()


if __name__ == "__main__":
    main()