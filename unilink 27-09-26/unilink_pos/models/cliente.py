from unilink_pos.config.conexion import get_db_connection


class Cliente:
    """Modelo de clientes para facturación."""

    def __init__(self, id_cliente=None, rif='', nombre='', telefono='', email='', direccion='', estado='activo'):
        self.id_cliente = id_cliente
        self.rif = rif
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.estado = estado

    @staticmethod
    def buscar_por_rif_o_nombre(texto: str):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        texto_like = f"%{texto}%"
        cursor.execute(
            "SELECT * FROM clientes WHERE rif LIKE %s OR nombre LIKE %s ORDER BY nombre ASC LIMIT 20",
            (texto_like, texto_like),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def guardar(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO clientes (rif, nombre, telefono, email, direccion, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (self.rif, self.nombre, self.telefono, self.email, self.direccion, self.estado),
        )
        self.id_cliente = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return self.id_cliente
