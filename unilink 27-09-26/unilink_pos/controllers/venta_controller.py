from decimal import Decimal

from unilink_pos.config.conexion import get_db_connection


class VentaController:
    """Controlador principal de ventas y facturación."""

    @staticmethod
    def calcular_totales(carrito, tasa_actual=36.0, iva_porcentaje=0.18):
        subtotal = sum(float(item["precio_venta"]) * int(item["cantidad"]) for item in carrito)
        iva = subtotal * float(iva_porcentaje)
        total = subtotal + iva
        total_local = total * float(tasa_actual)
        return {
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "total_local": total_local,
        }

    @staticmethod
    def registrar_venta(id_cliente, id_usuario, carrito, metodo_pago, tasa_actual=36.0, iva_porcentaje=0.18):
        conn = get_db_connection()
        cursor = conn.cursor()
        totales = VentaController.calcular_totales(carrito, tasa_actual, iva_porcentaje)

        cursor.execute(
            """
            INSERT INTO ventas (id_cliente, id_usuario, subtotal, iva, total, metodo_pago, estado)
            VALUES (%s, %s, %s, %s, %s, %s, 'completada')
            """,
            (id_cliente, id_usuario, Decimal(str(totales["subtotal"])), Decimal(str(totales["iva"])), Decimal(str(totales["total"])), metodo_pago),
        )
        id_venta = cursor.lastrowid

        for item in carrito:
            cursor.execute(
                """
                INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    id_venta,
                    item["id_producto"],
                    int(item["cantidad"]),
                    Decimal(str(item["precio_venta"])),
                    Decimal(str(float(item["precio_venta"]) * int(item["cantidad"]))),
                ),
            )
            cursor.execute(
                "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
                (int(item["cantidad"]), item["id_producto"]),
            )

        conn.commit()
        cursor.close()
        conn.close()
        return id_venta, totales

    @staticmethod
    def calcular_cambio(recibido, total):
        return max(0.0, float(recibido) - float(total))
