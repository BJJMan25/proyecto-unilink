import datetime
from fpdf import FPDF
from modelo.venta import Venta, DetalleVenta
from modelo.producto import Producto
from database.conexion import conectar_db
from config import BASE_DIR


IGV_PCT = 18

class VentaController:
    """
    Controlador para gestionar el proceso de ventas.
    Maneja el carrito de compras, cálculos de impuestos y generación de comprobantes PDF.
    """
    def __init__(self, usuario_id, nombre_usuario=""):
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario
        self.carrito = [] # Lista de diccionarios con productos seleccionados

    def buscar_producto(self, codigo_barras):
        """Busca un producto por su código de barras para añadirlo al carrito."""
        if not codigo_barras:
            return False, "Ingrese un código de barras", None

        producto = Producto.buscar_por_codigo(codigo_barras.strip())
        if not producto:
            return False, "Producto no encontrado", None

        if producto.stock_actual <= 0:
            return False, "Producto sin stock disponible", None

        return True, producto.nombre, producto

    def obtener_productos_disponibles(self):
        """Retorna una lista de productos que tienen stock mayor a cero."""
        productos = Producto.obtener_todos() or []
        productos_disponibles = []
        for p in productos:
            if p.stock_actual > 0:
                productos_disponibles.append(p)
        return productos_disponibles

    def obtener_total_ventas_hoy(self):
        """Retorna el total de ventas registradas hoy en MySQL."""
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT IFNULL(SUM(total), 0)
                    FROM ventas
                    WHERE DATE(fecha) = CURDATE()"""
                )
                row = cursor.fetchone()
                return float(row[0]) if row and row[0] is not None else 0.0
        except Exception as e:
            print(f"Error en VentaController.obtener_total_ventas_hoy: {e}")
            return 0.0

    def obtener_resumen_ventas_hoy(self):
        """Retorna un resumen simple de las ventas de hoy: cantidad y total."""
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT COUNT(*), IFNULL(SUM(total), 0)
                    FROM ventas
                    WHERE DATE(fecha) = CURDATE()"""
                )
                row = cursor.fetchone()
                cantidad = int(row[0]) if row and row[0] is not None else 0
                total = float(row[1]) if row and row[1] is not None else 0.0
                return cantidad, total
        except Exception as e:
            print(f"Error en VentaController.obtener_resumen_ventas_hoy: {e}")
            return 0, 0.0

    def agregar_al_carrito(self, producto, cantidad):
        """Añade un producto al carrito o actualiza su cantidad si ya existe."""

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0"

        # Validar stock disponible
        if cantidad > producto.stock_actual:
            return False, f"Stock insuficiente (disponible: {producto.stock_actual})"

        # Si el producto ya está en el carrito, actualizar cantidad
        for item in self.carrito:
            if item["producto_id"] == producto.id:
                nueva_cant = item["cantidad"] + cantidad
                if nueva_cant > producto.stock_actual:
                    return False, f"Stock insuficiente (disponible: {producto.stock_actual})"
                item["cantidad"] = nueva_cant
                item["subtotal"] = round(item["precio_unitario"] * nueva_cant, 2)
                return True, "Cantidad actualizada"

        # Si es nuevo, agregarlo a la lista
        self.carrito.append({
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "precio_unitario": producto.precio,
            "cantidad": cantidad,
            "subtotal": round(producto.precio * cantidad, 2)
        })
        return True, "Producto agregado"

    def agregar_por_id(self, producto_id, cantidad):
        """Busca un producto por ID y lo añade al carrito."""
        producto = Producto.buscar_por_id(producto_id)
        if not producto:
            return False, "Producto no encontrado"
        if producto.stock_actual <= 0:
            return False, "Sin stock"
        return self.agregar_al_carrito(producto, cantidad)

    def quitar_del_carrito(self, index):
        """Elimina un elemento del carrito por su índice en la lista."""
        if 0 <= index < len(self.carrito):
            self.carrito.pop(index)
            return True, "Producto quitado"
        return False, "Seleccione un producto"

    def obtener_subtotal(self):
        """Calcula la suma de los subtotales de todos los items en el carrito."""
        subtotal = 0
        for item in self.carrito:
            subtotal += item["subtotal"]
        return round(subtotal, 2)

    def obtener_igv(self):
        """Calcula el impuesto (IGV) basado en el subtotal."""
        return round(self.obtener_subtotal() * IGV_PCT / 100, 2)

    def obtener_total(self):
        """Calcula el total final (Subtotal + IGV)."""
        return round(self.obtener_subtotal() + self.obtener_igv(), 2)

    def calcular_vuelto(self, monto_pagado):
        """Calcula el cambio a entregar al cliente."""
        try:
            monto = float(monto_pagado)
        except ValueError:
            return False, "Monto inválido", 0

        total = self.obtener_total()
        if monto < total:
            return False, "Monto insuficiente", 0

        vuelto = round(monto - total, 2)
        return True, "OK", vuelto

    def realizar_venta(self):
        """Calcula totales, guarda la venta en la BD y prepara datos para el PDF."""
        if not self.carrito:
            return False, "El carrito está vacío", None

        try:
            # Calcular totales (responsabilidad del Controller)
            subtotal = self.obtener_subtotal()
            igv = self.obtener_igv()
            total = self.obtener_total()

            # Convertir carrito a objetos DetalleVenta
            detalles = [
                DetalleVenta(
                    producto_id=item["producto_id"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio_unitario"],
                    subtotal=item["subtotal"]
                ) for item in self.carrito
            ]

            # Registrar en la BD con valores ya calculados
            venta_id = Venta.crear(
                self.usuario_id, detalles, subtotal, igv, total
            )
            if not venta_id:
                return False, "No se pudo registrar la venta", None
            
            # Preparar datos para el PDF
            datos_pdf = {
                "venta_id": venta_id,
                "usuario": self.nombre_usuario,
                "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "items": list(self.carrito),
                "subtotal": subtotal,
                "igv": igv,
                "igv_pct": IGV_PCT,
                "total": total
            }
            self.carrito.clear() # Limpiar carrito tras éxito
            return True, f"Venta #{venta_id} realizada", datos_pdf
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def limpiar_carrito(self):
        """Vacía el carrito de compras."""
        self.carrito.clear()

    def generar_pdf(self, datos, monto_pagado, vuelto):
        """Genera un comprobante de pago en formato PDF."""
        ventas_dir = BASE_DIR / "ventas_pdf"
        ventas_dir.mkdir(exist_ok=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Encabezado
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Punto de Venta", align="C", new_x="LMARGIN", new_y="NEXT")

        # Info de la venta
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Venta #{datos['venta_id']}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Fecha: {datos['fecha']}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Cajero: {datos['usuario']}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Cabecera de tabla
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(70, 8, "Producto", border=1)
        pdf.cell(25, 8, "Cant.", border=1, align="C")
        pdf.cell(35, 8, "P. Unit.", border=1, align="C")
        pdf.cell(40, 8, "Subtotal", border=1, align="C")
        pdf.ln()

        # Detalle de productos
        pdf.set_font("Helvetica", "", 10)
        for item in datos["items"]:
            pdf.cell(70, 7, item["nombre"][:25], border=1)
            pdf.cell(25, 7, str(item["cantidad"]), border=1, align="C")
            pdf.cell(35, 7, f"S/ {item['precio_unitario']:.2f}", border=1, align="C")
            pdf.cell(40, 7, f"S/ {item['subtotal']:.2f}", border=1, align="C")
            pdf.ln()

        # Totales
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(130, 7, "Subtotal:", align="R")
        pdf.cell(40, 7, f"S/ {datos['subtotal']:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(130, 7, f"IGV ({datos['igv_pct']}%):", align="R")
        pdf.cell(40, 7, f"S/ {datos['igv']:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(130, 8, "TOTAL:", align="R")
        pdf.cell(40, 8, f"S/ {datos['total']:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        # Pago y Vuelto
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(130, 7, "Pagado:", align="R")
        pdf.cell(40, 7, f"S/ {monto_pagado:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.cell(130, 7, "Vuelto:", align="R")
        pdf.cell(40, 7, f"S/ {vuelto:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        # Guardar archivo
        nombre_archivo = f"venta_{datos['venta_id']}.pdf"
        ruta = str(ventas_dir / nombre_archivo)
        pdf.output(ruta)
        return ruta