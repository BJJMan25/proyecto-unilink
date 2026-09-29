"""Bootstrap modular del sistema Unilink POS.

Este módulo actúa como puente seguro entre la arquitectura modular moderna
(y que se está desarrollando bajo unilink_pos/) y la aplicación principal
estable que ya funciona en el proyecto real.
"""


def main():
    """Lanza la app principal verificada en la raíz del proyecto."""
    import main as app_main

    app_main.main()


if __name__ == "__main__":
    main()
