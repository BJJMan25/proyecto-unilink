import hashlib
import logging
from database.conexion import conectar_db

class Usuario:
    def __init__(self, id=None, nombre_completo=None, nombre_usuario=None, contrasena=None, rol_id=None, activo=1, fecha_creacion=None, rol_nombre=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.rol_id = rol_id
        self.activo = activo
        self.fecha_creacion = fecha_creacion
        self.rol_nombre = rol_nombre

    @staticmethod
    def _hash_password(contrasena):
        if not contrasena:
            return ""
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
    
    @staticmethod
    def autenticar(nombre_usuario, contrasena) -> 'Usuario | None':
        hashed = Usuario._hash_password(contrasena)

        with conectar_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute('''
                SELECT u.id, u.nombre_completo, u.nombre_usuario, u.contrasena, r.nombre AS rol_nombre, u.activo, u.rol_id
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                WHERE u.nombre_usuario = %s AND u.activo = 1
            ''', (nombre_usuario,))

            usuario = cursor.fetchone()
            
            if usuario:
                db_password = usuario['contrasena']
                if isinstance(db_password, bytes):
                    db_password = db_password.decode('utf-8')

                if db_password == hashed:
                    return Usuario(
                        id=usuario['id'],
                        nombre_completo=usuario['nombre_completo'],
                        nombre_usuario=usuario['nombre_usuario'],
                        contrasena=db_password,
                        rol_nombre=usuario['rol_nombre'],
                        activo=usuario['activo'],
                        rol_id=usuario['rol_id']
                    )
            
        return None
    
    @staticmethod
    def obtener_todos() -> list['Usuario']:
        with conectar_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT u.id, u.nombre_completo, u.nombre_usuario, r.nombre AS rol_nombre, u.activo, u.fecha_creacion
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
            ''')

            usuarios = []
            for u in cursor.fetchall():
                usuarios.append(Usuario(
                    id=u['id'],
                    nombre_completo=u['nombre_completo'],
                    nombre_usuario=u['nombre_usuario'],
                    rol_nombre=u['rol_nombre'],
                    activo=u['activo'],
                    fecha_creacion=u['fecha_creacion']
                ))
            
            return usuarios

    @staticmethod
    def obtener_por_id(usuario_id: int) -> 'Usuario | None':
        with conectar_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT u.id, u.nombre_completo, u.nombre_usuario, u.rol_id, r.nombre AS rol_nombre, u.activo, u.fecha_creacion
                FROM usuarios u
                JOIN roles r ON u.rol_id = r.id
                WHERE u.id = %s
            ''', (usuario_id,))

            u = cursor.fetchone()
            if not u:
                return None

            return Usuario(
                id=u['id'],
                nombre_completo=u['nombre_completo'],
                nombre_usuario=u['nombre_usuario'],
                rol_id=u['rol_id'],
                rol_nombre=u['rol_nombre'],
                activo=u['activo'],
                fecha_creacion=u['fecha_creacion']
            )

    def guardar(self) -> int | None:
        try:
            # CORRECCIÓN: Usamos una variable local para el hash. 
            # Así evitamos alterar 'self.contrasena' si ocurre un rollback o reintento.
            password_encriptada = Usuario._hash_password(self.contrasena)
            
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuarios (nombre_completo, nombre_usuario, contrasena, rol_id, activo)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (self.nombre_completo, self.nombre_usuario, password_encriptada, self.rol_id, self.activo))
                conn.commit()
                
                self.id = cursor.lastrowid
                self.contrasena = password_encriptada # Se actualiza la propiedad solo tras el commit exitoso
                return self.id
        except Exception as e:
            logging.error(f"Error al guardar usuario en la base de datos: {str(e)}")
            return None
        
    @staticmethod
    def cambiar_estado(usuario_id, estado) -> bool:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                # CORRECCIÓN: Garantizamos correspondencia con la columna 'id' de la tabla estructurada
                cursor.execute('''
                    UPDATE usuarios
                    SET activo = %s
                    WHERE id = %s
                ''', (estado, usuario_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error al cambiar estado del usuario {usuario_id}: {str(e)}")
            return False

    @staticmethod
    def actualizar_datos(usuario_id: int, nombre_completo: str, nombre_usuario: str, rol_id: int) -> bool:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios
                    SET nombre_completo = %s, nombre_usuario = %s, rol_id = %s
                    WHERE id = %s
                ''', (nombre_completo, nombre_usuario, rol_id, usuario_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error al actualizar datos del usuario {usuario_id}: {str(e)}")
            return False

    @staticmethod
    def actualizar_contrasena(usuario_id: int, nueva_contrasena: str) -> bool:
        try:
            password_encriptada = Usuario._hash_password(nueva_contrasena)
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios
                    SET contrasena = %s
                    WHERE id = %s
                ''', (password_encriptada, usuario_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error al actualizar contrasena del usuario {usuario_id}: {str(e)}")
            return False
        
    @staticmethod
    def obtener_roles() -> list[tuple]:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nombre FROM roles ORDER BY id ASC')
            return cursor.fetchall()