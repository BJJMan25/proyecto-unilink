from nlp_engine import NLPEngine


class AsistenteController:
    def __init__(self, vista, producto_controller=None, venta_controller=None):
        self.vista = vista
        self.producto_controller = producto_controller
        self.venta_controller = venta_controller
        self.nlp_engine = NLPEngine()

    def procesar_mensaje(self, texto):
        resultado = self.nlp_engine.analizar(texto)
        intencion = resultado.get("intencion")
        argumento = resultado.get("argumento")

        if intencion == "ir_a":
            self._respuesta_ir_a(argumento)
        elif intencion == "buscar_producto":
            self._respuesta_buscar_producto(argumento)
        elif intencion == "stock_bajo":
            self._respuesta_stock_bajo()
        elif intencion == "ver_ventas":
            self._respuesta_ver_ventas(argumento)
        elif intencion == "saludo":
            self._respuesta_saludo()
        elif intencion == "despedida":
            self._respuesta_despedida()
        elif intencion == "ninguna":
            self._mostrar_respuesta("Por favor escribe un comando válido.")
        else:
            self._mostrar_respuesta(
                "No entendí tu solicitud. Prueba con: '¿Stock bajo?', '¿Ventas de hoy?' o 'Ir a Productos'."
            )

    def _respuesta_ir_a(self, argumento):
        if "producto" in argumento or "productos" in argumento:
            # Ejemplo: cambiar a la pantalla de productos
            self._mostrar_respuesta("Mostrando Inventario. Navega a Productos para ver la lista de artículos.")
            # TODO: llamar a ProductoController desde aqui para cargar la vista de productos
            # self.vista.master._mostrar_productos()
            return

        if "venta" in argumento or "ventas" in argumento:
            self._mostrar_respuesta("Mostrando el módulo de Ventas. Allí puedes procesar cobros y ver el carrito.")
            # TODO: llamar a VentaController desde aqui para cargar la vista de ventas
            # self.vista.master._mostrar_ventas()
            return

        self._mostrar_respuesta(
            "¿A qué módulo quieres ir? Por ejemplo: 'Ir a Productos' o 'Ir a Ventas'."
        )

    def _respuesta_buscar_producto(self, argumento):
        if not argumento:
            self._mostrar_respuesta("Dime el nombre o el código del producto que quieres buscar.")
            return

        productos = []
        if self.producto_controller:
            productos = self.producto_controller.buscar_producto_por_nombre(argumento)

        if productos:
            lines = []
            for producto in productos[:5]:
                lines.append(
                    f"{producto.nombre} | Código: {producto.codigo_barras} | Stock: {producto.stock_actual}"
                )
            self._mostrar_respuesta("Encontré estos productos:\n" + "\n".join(lines))
        else:
            self._mostrar_respuesta(
                "No encontré productos que coincidan con ese término en la base de datos."
            )

    def _respuesta_stock_bajo(self):
        productos = []
        if self.producto_controller:
            productos = self.producto_controller.obtener_productos_stock_bajo(limite=5)

        if productos:
            lines = []
            for producto in productos[:5]:
                lines.append(
                    f"{producto.nombre} | Código: {producto.codigo_barras} | Stock: {producto.stock_actual}"
                )
            self._mostrar_respuesta(
                "Productos con stock bajo:\n" + "\n".join(lines)
            )
        else:
            self._mostrar_respuesta(
                "No hay productos con stock bajo en la base de datos o no hay datos disponibles."
            )

    def _respuesta_ver_ventas(self, argumento):
        if self.venta_controller:
            cantidad, total = self.venta_controller.obtener_resumen_ventas_hoy()
            self._mostrar_respuesta(
                f"Ventas de hoy: {cantidad} transacción(es), total S/ {total:.2f}."
            )
        else:
            self._mostrar_respuesta(
                "No pude acceder a los datos de ventas. Asegúrate de que la conexión a base de datos esté disponible."
            )

    def _respuesta_saludo(self):
        self._mostrar_respuesta(
            "Hola, soy tu asistente local de UNILINK. Puedes preguntar por stock, ventas o ir a un módulo.")

    def _respuesta_despedida(self):
        self._mostrar_respuesta("Hasta pronto. Si necesitas ayuda, escribe otro comando.")

    def _mostrar_respuesta(self, texto):
        if self.vista:
            self.vista.agregar_mensaje_asistente(texto)
