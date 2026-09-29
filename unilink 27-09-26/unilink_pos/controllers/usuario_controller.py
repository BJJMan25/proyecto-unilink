from typing import Tuple

from unilink_pos.models.usuario import Usuario


class UsuarioController:
    """Controlador de autenticación y gestión de usuarios."""

    def __init__(self):
        self.usuario_actual = None

    def login(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Complete usuario y contraseña."

        usuario = Usuario.autenticar(username, password)
        if not usuario:
            return False, "Credenciales inválidas."

        self.usuario_actual = usuario
        return True, "Inicio de sesión correcto."

    def cerrar_sesion(self):
        self.usuario_actual = None

    def obtener_roles(self):
        return Usuario.obtener_roles()

    def obtener_usuarios(self):
        return Usuario.obtener_todos()

    def registrar_usuario(self, nombre_completo: str, usuario: str, password: str, id_rol: int):
        if not nombre_completo or not usuario or not password:
            return False, "Complete todos los campos."
        if len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."
        nuevo = Usuario(
            nombre_completo=nombre_completo,
            usuario=usuario,
            password=password,
            id_rol=id_rol,
            estado=1,
        )
        id_creado = nuevo.guardar()
        if not id_creado:
            return False, "No se pudo registrar el usuario."
        return True, "Usuario registrado correctamente."

    def cambiar_estado(self, id_usuario: int, estado: int):
        return Usuario.cambiar_estado(id_usuario, estado)

    def editar_usuario(self, id_usuario: int, nombre_completo: str, usuario: str, id_rol: int):
        if not nombre_completo or not usuario:
            return False, "Datos incompletos."
        Usuario.actualizar_datos(id_usuario, nombre_completo, usuario, id_rol)
        return True, "Usuario actualizado."

    def editar_contrasena(self, id_usuario: int, nueva_password: str):
        if len(nueva_password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."
        Usuario.actualizar_contrasena(id_usuario, nueva_password)
        return True, "Contraseña actualizada."

    def permisos_del_rol_actual(self):
        if not self.usuario_actual:
            return []
        return Usuario.obtener_permisos_por_rol(self.usuario_actual.id_rol)
