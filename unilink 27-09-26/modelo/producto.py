from database.conexion import conectar_db

class Producto:
    def __init__(self, id=None, codigo_barras=None, nombre=None, precio=None, stock_actual=None):
        self.id = id
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.precio = precio
        self.stock_actual = stock_actual

    # Guardar y actualizar producto 
    def guardar(self) -> bool | None:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                if self.id is None:
                    cursor.execute(
                        """INSERT INTO productos (codigo_barras, nombre, precio_venta, stock)
                        VALUES (%s, %s, %s, %s)""",
                        (self.codigo_barras, self.nombre, self.precio, self.stock_actual)
                    )
                else:
                    cursor.execute(
                        """UPDATE productos SET codigo_barras = %s, nombre = %s, precio_venta = %s, stock = %s
                        WHERE id_producto = %s""",
                        (self.codigo_barras, self.nombre, self.precio, self.stock_actual, self.id)
                    )
                conn.commit()
                if self.id is None:
                    self.id = cursor.lastrowid
                return True
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            print(f"Error en Producto.guardar: {e}")
            return None

    # Obtener la lista de productos
    @staticmethod
    def obtener_todos() -> list['Producto']:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id_producto, codigo_barras, nombre, precio_venta, stock
                    FROM productos ORDER BY id_producto"""
                )
                rows = cursor.fetchall()
                productos_list = []
                if rows:
                    for row in rows:
                        productos_list.append(Producto(
                            id=row[0],
                            codigo_barras=row[1],
                            nombre=row[2],
                            precio=row[3],
                            stock_actual=row[4]
                        ))
                return productos_list
        except Exception as e:
            print(f"Error en Producto.obtener_todos: {e}")
            return []

    # Eliminar producto
    @staticmethod
    def eliminar(producto_id) -> bool | None:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM productos WHERE id_producto = %s", (producto_id,))
                conn.commit()
                return True
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            print(f"Error en Producto.eliminar: {e}")
            return None
    
    @staticmethod
    def aumentar_stock(producto_id, cantidad) -> bool:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE productos SET stock = stock + %s WHERE id_producto = %s",
                    (cantidad, producto_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error en Producto.aumentar_stock: {e}")
            return False
    
    # Buscar producto por código de barras
    @staticmethod
    def buscar_por_codigo(codigo_barras) -> 'Producto | None':
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id_producto, codigo_barras, nombre, precio_venta, stock
                    FROM productos WHERE codigo_barras = %s""",
                    (codigo_barras,)
                )
                row = cursor.fetchone()
                if row:
                    return Producto(
                        id=row[0],
                        codigo_barras=row[1],
                        nombre=row[2],
                        precio=row[3],
                        stock_actual=row[4]
                    )
                return None
        except Exception as e:
            print(f"Error en Producto.buscar_por_codigo: {e}")
            return None

    @staticmethod
    def buscar_por_nombre(nombre) -> list['Producto']:
        try:
            termino = f"%{nombre.strip()}%"
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id_producto, codigo_barras, nombre, precio_venta, stock
                    FROM productos
                    WHERE nombre LIKE %s OR codigo_barras LIKE %s
                    ORDER BY stock ASC, nombre ASC""",
                    (termino, termino)
                )
                rows = cursor.fetchall()
                resultados = []
                for row in rows:
                    resultados.append(Producto(
                        id=row[0],
                        codigo_barras=row[1],
                        nombre=row[2],
                        precio=row[3],
                        stock_actual=row[4]
                    ))
                return resultados
        except Exception as e:
            print(f"Error en Producto.buscar_por_nombre: {e}")
            return []

    @staticmethod
    def obtener_stock_bajo(limite=5) -> list['Producto']:
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id_producto, codigo_barras, nombre, precio_venta, stock
                    FROM productos
                    WHERE stock <= %s
                    ORDER BY stock ASC, nombre ASC""",
                    (limite,)
                )
                rows = cursor.fetchall()
                productos_list = []
                for row in rows:
                    productos_list.append(Producto(
                        id=row[0],
                        codigo_barras=row[1],
                        nombre=row[2],
                        precio=row[3],
                        stock_actual=row[4]
                    ))
                return productos_list
        except Exception as e:
            print(f"Error en Producto.obtener_stock_bajo: {e}")
            return []

    @staticmethod
    def buscar_por_id(producto_id) -> 'Producto | None':
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT id_producto, codigo_barras, nombre, precio_venta, stock
                    FROM productos WHERE id_producto = %s""",
                    (producto_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Producto(
                        id=row[0],
                        codigo_barras=row[1],
                        nombre=row[2],
                        precio=row[3],
                        stock_actual=row[4]
                    )
                return None
        except Exception as e:
            print(f"Error en Producto.buscar_por_id: {e}")
            return None