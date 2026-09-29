CREATE DATABASE IF NOT EXISTS unilink
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;

USE unilink;

CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL
);

CREATE TABLE proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    pais_origen  VARCHAR(50),
    telefono     VARCHAR(20),
    email        VARCHAR(100)
);

CREATE TABLE productos (
    id_producto   INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(150) NOT NULL,
    descripcion   TEXT,
    precio_compra DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    precio_venta  DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock         INT          NOT NULL DEFAULT 0,
    id_categoria  INT,
    id_proveedor  INT,
    codigo_barras VARCHAR(50),
    estado        VARCHAR(20)  NOT NULL DEFAULT 'activo',
    fecha_creacion DATETIME    DEFAULT NOW(),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    telefono   VARCHAR(20),
    email      VARCHAR(100),
    direccion  VARCHAR(150),
    ciudad     VARCHAR(50),
    estado     VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE ventas (
    id_venta    INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente  INT,
    fecha       DATETIME     DEFAULT NOW(),
    total       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    metodo_pago VARCHAR(50),
    estado      VARCHAR(20)  NOT NULL DEFAULT 'completada',
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE detalle_ventas (
    id_detalle      INT AUTO_INCREMENT PRIMARY KEY,
    id_venta        INT NOT NULL,
    id_producto     INT NOT NULL,
    cantidad        INT          NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(12,2) NOT NULL,
    subtotal        DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (id_venta)    REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE movimientos_inventario (
    id_movimiento   INT AUTO_INCREMENT PRIMARY KEY,
    id_producto     INT NOT NULL,
    tipo_movimiento VARCHAR(10) NOT NULL COMMENT 'Entrada o Salida',
    cantidad        INT         NOT NULL,
    fecha           DATETIME    DEFAULT NOW(),
    descripcion     VARCHAR(150),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE usuarios (
    id_usuario     INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    usuario        VARCHAR(50)  NOT NULL UNIQUE,
    password       VARCHAR(64)  NOT NULL,
    rol            VARCHAR(20)  NOT NULL DEFAULT 'vendedor',
    estado         VARCHAR(20)  NOT NULL DEFAULT 'activo',
    fecha_creacion DATETIME     DEFAULT NOW()
);
