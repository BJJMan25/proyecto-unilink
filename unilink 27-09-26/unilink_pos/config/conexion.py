import mysql.connector
from mysql.connector import Error as MySQLError


class DatabaseConnection:
    """Gestión central de conexión MySQL para Unilink POS."""

    DB_NAME = "unilink_pos"

    def __init__(self, host="localhost", user="root", password="", database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database or self.DB_NAME

    def connect(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
                charset="utf8mb4",
                use_pure=True,
            )
        except mysql.connector.Error as exc:
            if exc.errno == 1049:
                self.initialize()
                return mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=True,
                    charset="utf8mb4",
                    use_pure=True,
                )
            raise

    def connect_server(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            autocommit=True,
            charset="utf8mb4",
            use_pure=True,
        )

    def initialize(self):
        try:
            server = self.connect_server()
            cursor = server.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            server.close()

            conn = self.connect()
            cursor = conn.cursor()

            schema = [
                """
                CREATE TABLE IF NOT EXISTS roles (
                    id_rol INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    descripcion VARCHAR(200) DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS permisos (
                    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(80) NOT NULL UNIQUE,
                    descripcion VARCHAR(200) DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS rol_permisos (
                    id_rol INT NOT NULL,
                    id_permiso INT NOT NULL,
                    PRIMARY KEY (id_rol, id_permiso),
                    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
                    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_completo VARCHAR(150) NOT NULL,
                    usuario VARCHAR(80) NOT NULL UNIQUE,
                    password VARCHAR(128) NOT NULL,
                    id_rol INT NOT NULL,
                    estado TINYINT DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS productos (
                    id_producto INT AUTO_INCREMENT PRIMARY KEY,
                    codigo_barras VARCHAR(80) NOT NULL UNIQUE,
                    nombre VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    precio_compra DECIMAL(12,2) NOT NULL DEFAULT 0,
                    precio_venta DECIMAL(12,2) NOT NULL DEFAULT 0,
                    stock INT NOT NULL DEFAULT 0,
                    stock_minimo INT NOT NULL DEFAULT 0,
                    categoria VARCHAR(120) DEFAULT 'Sin categoría',
                    estado VARCHAR(20) DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                    rif VARCHAR(30) DEFAULT '',
                    nombre VARCHAR(150) NOT NULL,
                    telefono VARCHAR(30) DEFAULT '',
                    email VARCHAR(120) DEFAULT '',
                    direccion VARCHAR(200) DEFAULT '',
                    estado VARCHAR(20) DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS ventas (
                    id_venta INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT,
                    id_usuario INT,
                    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
                    iva DECIMAL(12,2) NOT NULL DEFAULT 0,
                    total DECIMAL(12,2) NOT NULL DEFAULT 0,
                    metodo_pago VARCHAR(50) DEFAULT 'Efectivo',
                    estado VARCHAR(30) DEFAULT 'completada',
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
                    id_venta INT NOT NULL,
                    id_producto INT NOT NULL,
                    cantidad INT NOT NULL,
                    precio_unitario DECIMAL(12,2) NOT NULL,
                    subtotal DECIMAL(12,2) NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
                    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS tasas_cambio (
                    id_tasa INT AUTO_INCREMENT PRIMARY KEY,
                    moneda_origen VARCHAR(10) NOT NULL,
                    moneda_destino VARCHAR(10) NOT NULL,
                    valor DECIMAL(10,4) NOT NULL,
                    fuente VARCHAR(50) NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS logs_auditoria (
                    id_log INT AUTO_INCREMENT PRIMARY KEY,
                    accion VARCHAR(120) NOT NULL,
                    descripcion TEXT NOT NULL,
                    id_usuario INT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
                """
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    id_config INT AUTO_INCREMENT PRIMARY KEY,
                    rif_empresa VARCHAR(50) DEFAULT '',
                    nombre_empresa VARCHAR(150) DEFAULT 'Unilink POS',
                    direccion VARCHAR(200) DEFAULT '',
                    telefono VARCHAR(30) DEFAULT '',
                    iva DECIMAL(6,4) DEFAULT 0.1800,
                    moneda_local VARCHAR(10) DEFAULT 'VES',
                    moneda_externa VARCHAR(10) DEFAULT 'USD',
                    ultimo_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """,
            ]

            for statement in schema:
                cursor.execute(statement)

            cursor.execute("SELECT COUNT(*) FROM roles")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    "INSERT INTO roles (id_rol, nombre, descripcion) VALUES (%s, %s, %s)",
                    [
                        (1, "Administrador", "Acceso total al sistema"),
                        (2, "Empleador", "Inventario, ventas y reportes"),
                        (3, "Empleado", "Ventas y cobro"),
                    ],
                )

            cursor.execute("SELECT COUNT(*) FROM permisos")
            if cursor.fetchone()[0] == 0:
                permisos = [
                    ("usuarios_ver", "Ver usuarios"),
                    ("usuarios_editar", "Editar usuarios"),
                    ("inventario_ver", "Ver inventario"),
                    ("inventario_editar", "Editar inventario"),
                    ("ventas_ver", "Ver ventas"),
                    ("ventas_editar", "Procesar ventas"),
                    ("reportes_ver", "Ver reportes"),
                    ("ajustes_ver", "Ver ajustes"),
                ]
                cursor.executemany(
                    "INSERT INTO permisos (nombre, descripcion) VALUES (%s, %s)",
                    permisos,
                )

            conn.commit()
            cursor.close()
            conn.close()
            print("[DB] Base de datos unilink_pos inicializada correctamente.")

        except MySQLError as exc:
            raise RuntimeError(f"Error al inicializar la base de datos: {exc}") from exc


def get_db_connection():
    conn = DatabaseConnection().connect()
    return conn


if __name__ == "__main__":
    DatabaseConnection().initialize()
