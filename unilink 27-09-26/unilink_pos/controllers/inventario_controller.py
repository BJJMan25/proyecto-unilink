from unilink_pos.models.producto import Producto


class InventarioController:
    """Controlador para catálogo, stock y movimientos."""

    def obtener_productos(self):
        return Producto.obtener_todos()

    def buscar_productos(self, texto: str):
        return Producto.buscar_por_texto(texto)

    def registrar_producto(self, producto_data):
        producto = Producto(
            codigo_barras=producto_data["codigo_barras"],
            nombre=producto_data["nombre"],
            descripcion=producto_data.get("descripcion", ""),
            precio_compra=float(producto_data.get("precio_compra", 0)),
            precio_venta=float(producto_data.get("precio_venta", 0)),
            stock=int(producto_data.get("stock", 0)),
            stock_minimo=int(producto_data.get("stock_minimo", 0)),
            categoria=producto_data.get("categoria", "Sin categoría"),
            estado=producto_data.get("estado", "activo"),
        )
        return producto.guardar()

    def stock_critico(self):
        return Producto.obtener_stock_critico()

    def ajustar_stock(self, id_producto: int, delta: int):
        return Producto.actualizar_stock(id_producto, delta)
