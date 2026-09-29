from typing import Optional

from unilink_pos.config.conexion import get_db_connection


class Producto:
    """Modelo del catálogo de productos del POS."""

    def __init__(self, id_producto=None, codigo_barras=None, nombre=None, descripcion=None,
                 precio_compra=0.0, precio_venta=0.0, stock=0, stock_minimo=0,
                 categoria='Sin categoría', estado='activo'):
        self.id_producto = id_producto
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.categoria = categoria
        self.estado = estado

    @staticmethod
    def obtener_todos():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY nombre ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def buscar_por_texto(texto: str):
        texto = f"%{texto}%"
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM productos WHERE codigo_barras LIKE %s OR nombre LIKE %s ORDER BY nombre ASC",
            (texto, texto),
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
            INSERT INTO productos (codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock, stock_minimo, categoria, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self.codigo_barras,
                self.nombre,
                self.descripcion,
                self.precio_compra,
                self.precio_venta,
                self.stock,
                self.stock_minimo,
                self.categoria,
                self.estado,
            ),
        )
        self.id_producto = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return self.id_producto

    @staticmethod
    def actualizar_stock(id_producto: int, cantidad: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s", (cantidad, id_producto))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def obtener_stock_critico():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE stock <= stock_minimo ORDER BY stock ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
