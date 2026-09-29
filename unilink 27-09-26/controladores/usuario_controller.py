from modelo.usuario import Usuario

class UsuarioController:

    def __init__(self):
        self.usuario_actual = None

    def login(self, nombre_usuario, contrasena) -> bool | str:
        if not nombre_usuario or not contrasena:
            return False, 'Complete los campos para iniciar sesión.'
        
        usuario = Usuario.autenticar(nombre_usuario, contrasena)
        if usuario:
            self.usuario_actual = usuario
            return True, 'Inicio de sesión exitoso.'
        
        return False, 'Nombre de usuario o contraseña incorrectos.'


    def cerrar_sesion(self):
        self.usuario_actual = None

    def obtener_usuarios(self) -> list[Usuario]:
        if not self.usuario_actual or not self.usuario_actual.rol_id == 1:  # Solo el admin puede ver la lista de usuarios
            return []
        
        return Usuario.obtener_todos()
    
    def registrar_usuario(self, usuario:Usuario, confirmar_contrasena:str) -> tuple[bool, str]:

        if not self.usuario_actual or not self.usuario_actual.rol_id == 1:  # Solo el admin puede registrar nuevos usuarios
            return False, 'No tienes permiso para registrar nuevos usuarios.'
        
        # Validaciones de campos
        if not usuario.nombre_completo or not usuario.nombre_usuario or not usuario.contrasena or not confirmar_contrasena:
            return False, "Complete todos los campos"
        
        if len(usuario.nombre_completo) < 3:
            return False, "El nombre completo debe tener al menos 3 caracteres"

        if len(usuario.nombre_usuario) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"

        if usuario.contrasena != confirmar_contrasena:
            return False, "Las contraseñas no coinciden"

        if len(usuario.contrasena) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres"
        
        try:
            usuario_id = usuario.guardar()
            if not usuario_id:
                return False, "No se pudo guardar el usuario"
            return True, "Usuario registrado exitosamente"
        except Exception as e:
            if "UNIQUE" in str(e).upper():
                return False, "El nombre de usuario ya existe"
            return False, "Error al registrar el usuario"

    def obtener_usuario_por_id(self, usuario_id: int):
        if not self.usuario_actual or self.usuario_actual.rol_id != 1:
            return None
        return Usuario.obtener_por_id(usuario_id)

    def editar_usuario(self, usuario: Usuario) -> tuple[bool, str]:
        if not self.usuario_actual or self.usuario_actual.rol_id != 1:
            return False, "No tienes permiso para editar usuarios"

        if not usuario.id:
            return False, "Usuario invalido"

        if not usuario.nombre_completo or not usuario.nombre_usuario or not usuario.rol_id:
            return False, "Complete todos los campos"

        if len(usuario.nombre_completo) < 3:
            return False, "El nombre completo debe tener al menos 3 caracteres"

        if len(usuario.nombre_usuario) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"

        exito = Usuario.actualizar_datos(
            usuario.id,
            usuario.nombre_completo,
            usuario.nombre_usuario,
            usuario.rol_id
        )

        if not exito:
            return False, "No se pudo actualizar el usuario"

        return True, "Usuario actualizado correctamente"

    def editar_contrasena_usuario(self, usuario_id: int, nueva_contrasena: str, confirmar_contrasena: str) -> tuple[bool, str]:
        if not self.usuario_actual or self.usuario_actual.rol_id != 1:
            return False, "No tienes permiso para editar contrasenas"

        if not usuario_id:
            return False, "Usuario invalido"

        if not nueva_contrasena or not confirmar_contrasena:
            return False, "Complete todos los campos"

        if nueva_contrasena != confirmar_contrasena:
            return False, "Las contrasenas no coinciden"

        if len(nueva_contrasena) < 4:
            return False, "La contrasena debe tener al menos 4 caracteres"

        exito = Usuario.actualizar_contrasena(usuario_id, nueva_contrasena)
        if not exito:
            return False, "No se pudo actualizar la contrasena"

        return True, "Contrasena actualizada correctamente"
        
    
    def obtener_roles(self) -> list[tuple]:
        return Usuario.obtener_roles()
    
    def cambiar_estado_usuario(self, usuario_id, estado):
        if not self.usuario_actual or not self.usuario_actual.rol_id == 1:  
            return False, "Sin permisos"
        
        if usuario_id == self.usuario_actual.id:
            return False, "No puedes cambiar el estado de tu propio usuario"
        
        Usuario.cambiar_estado(usuario_id, estado)
        if estado:
            estado = "activado"
        else:
            estado = "desactivado"
        return True, f"Usuario {estado} correctamente"