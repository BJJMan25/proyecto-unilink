import hashlib
import logging
from typing import Optional

from unilink_pos.config.conexion import get_db_connection


class Usuario:
    """Modelo de usuario con autenticación segura y permisos."""

    def __init__(self, id_usuario=None, nombre_completo=None, usuario=None, password=None, id_rol=None, estado=1, fecha_creacion=None):
        self.id_usuario = id_usuario
        self.nombre_completo = nombre_completo
        self.usuario = usuario
        self.password = password
        self.id_rol = id_rol
        self.estado = estado
        self.fecha_creacion = fecha_creacion

    @staticmethod
    def _hash_password(password: str) -> str:
        if not password:
            return ""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def autenticar(usuario: str, password: str):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.*, r.nombre AS rol_nombre
            FROM usuarios u
            JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.usuario = %s AND u.estado = 1
            """,
            (usuario,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        if row["password"] == Usuario._hash_password(password):
            return Usuario(
                id_usuario=row["id_usuario"],
                nombre_completo=row["nombre_completo"],
                usuario=row["usuario"],
                id_rol=row["id_rol"],
                estado=row["estado"],
                fecha_creacion=row["fecha_creacion"],
            )
        return None

    @staticmethod
    def obtener_por_id(usuario_id: int):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE id_usuario = %s",
            (usuario_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return None
        return Usuario(
            id_usuario=row["id_usuario"],
            nombre_completo=row["nombre_completo"],
            usuario=row["usuario"],
            id_rol=row["id_rol"],
            estado=row["estado"],
            fecha_creacion=row["fecha_creacion"],
        )

    @staticmethod
    def obtener_todos():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.*, r.nombre AS rol_nombre
            FROM usuarios u
            JOIN roles r ON r.id_rol = u.id_rol
            ORDER BY u.id_usuario ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_roles():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_rol, nombre FROM roles ORDER BY id_rol ASC")
        roles = cursor.fetchall()
        cursor.close()
        conn.close()
        return roles

    def guardar(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO usuarios (nombre_completo, usuario, password, id_rol, estado)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (self.nombre_completo, self.usuario, self._hash_password(self.password), self.id_rol, self.estado),
            )
            self.id_usuario = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return self.id_usuario
        except Exception as exc:
            logging.exception("Error al guardar usuario")
            return None

    @staticmethod
    def cambiar_estado(usuario_id: int, estado: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET estado = %s WHERE id_usuario = %s", (estado, usuario_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def actualizar_datos(usuario_id: int, nombre_completo: str, usuario: str, id_rol: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET nombre_completo = %s, usuario = %s, id_rol = %s WHERE id_usuario = %s",
            (nombre_completo, usuario, id_rol, usuario_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def actualizar_contrasena(usuario_id: int, nueva_password: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET password = %s WHERE id_usuario = %s",
            (Usuario._hash_password(nueva_password), usuario_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def obtener_permisos_por_rol(id_rol: int):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.nombre
            FROM rol_permisos rp
            JOIN permisos p ON p.id_permiso = rp.id_permiso
            WHERE rp.id_rol = %s
            """,
            (id_rol,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row["nombre"] for row in rows]
