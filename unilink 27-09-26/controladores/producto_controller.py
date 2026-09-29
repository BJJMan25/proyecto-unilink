from modelo.producto import Producto

class ProductoController:

    def registrar_producto(self, producto):
        if not producto.codigo_barras or not producto.nombre or producto.precio is None or producto.stock_actual is None:
            return False, "Complete todos los campos"

        if len(str(producto.codigo_barras)) < 3:
            return False, "El codigo de barras debe tener al menos 3 caracteres"

        if len(producto.nombre) < 3:
            return False, "El nombre debe tener al menos 3 caracteres"

        try:
            producto.precio = float(producto.precio)
            producto.stock_actual = int(producto.stock_actual)
        except ValueError:
            return False, "Precio y stock deben ser valores numéricos"

        if producto.precio < 0:
            return False, "El precio debe ser mayor o igual a 0"

        if producto.stock_actual < 0:
            return False, "El stock actual debe ser mayor o igual a 0"

        try:
            resultado = producto.guardar()
            if resultado:
                return True, "Producto registrado exitosamente"
            else:
                return False, "No se pudo guardar el producto"
        except Exception as e:
            if "UNIQUE" in str(e):
                return False, "El codigo de barras ya existe"
            return False, f"Error: {str(e)}"
        
    def obtener_productos(self):
        return Producto.obtener_todos()

    def buscar_producto_por_nombre(self, termino):
        if not termino:
            return []
        return Producto.buscar_por_nombre(termino)

    def obtener_productos_stock_bajo(self, limite=5):
        return Producto.obtener_stock_bajo(limite)

    def agregar_stock(self, producto_id, cantidad):
        if not producto_id:
            return False, "Seleccione un producto válido"

        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return False, "Ingrese una cantidad numérica"

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0"

        exito = Producto.aumentar_stock(producto_id, cantidad)
        if not exito:
            return False, "No se pudo actualizar el stock"

        return True, "Stock actualizado correctamente"

    def actualizar_producto(self, producto):
        if not producto.codigo_barras or not producto.nombre or producto.precio is None or producto.stock_actual is None:
            return False, "Complete todos los campos"

        if len(str(producto.codigo_barras)) < 3:
            return False, "El codigo de barras debe tener al menos 3 caracteres"

        if len(producto.nombre) < 3:
            return False, "El nombre debe tener al menos 3 caracteres"

        try:
            producto.precio = float(producto.precio)
            producto.stock_actual = int(producto.stock_actual)
        except ValueError:
            return False, "Precio y stock deben ser valores numéricos"

        if producto.precio < 0:
            return False, "El precio debe ser mayor o igual a 0"

        if producto.stock_actual < 0:
            return False, "El stock actual debe ser mayor o igual a 0"

        try:
            resultado = producto.guardar()
            if resultado:
                return True, "Producto actualizado exitosamente"
            else:
                return False, "No se pudo actualizar el producto"
        except Exception as e:
            if "UNIQUE" in str(e):
                return False, "El codigo de barras ya existe"
            return False, f"Error: {str(e)}"

    def eliminar_producto(self, producto_id):
        if not producto_id:
            return False, "Seleccione un producto"

        resultado = Producto.eliminar(producto_id)
        if resultado:
            return True, "Producto eliminado exitosamente"
        return False, "Error al eliminar el producto"

    def obtener_producto_por_id(self, producto_id):
        return Producto.buscar_por_id(producto_id)