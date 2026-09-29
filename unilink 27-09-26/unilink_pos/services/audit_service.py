from unilink_pos.config.conexion import get_db_connection


def registrar_evento(id_usuario, accion, detalle):
    """Registra eventos de seguridad, ventas o mantenimiento en la bitácora."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs_auditoria (accion, descripcion, id_usuario, fecha) VALUES (%s, %s, %s, NOW())",
        (accion, detalle, id_usuario),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True
