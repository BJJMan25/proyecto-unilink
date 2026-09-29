from pathlib import Path
import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "unilink"
SCHEMA_PATH = Path(__file__).resolve().parent / "unilink.sql"

def conectar_server():
    """Establece conexión inicial con el servidor MySQL (sin especificar la BD)."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        timeout=5
    )

def conectar_db():
    """
    Conecta a la base de datos 'unilink'. 
    Si no existe en el servidor, la crea y le carga el archivo 'unilink.sql'.
    """
    try:
        # 1. Intentar conexión directa a la base de datos
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conexion

    except mysql.connector.Error as err:
        # Error 1049: Significa que la base de datos 'unilink' aún no existe
        if err.errno == 1049:
            print(f"-> La base de datos '{DB_NAME}' no existe. Creándola e inicializándola...")
            try:
                # 2. Conectar al servidor para crear la base de datos limpia
                conn_server = conectar_server()
                cursor = conn_server.cursor()
                cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn_server.close()
                
                # 3. Conectar a la nueva BD e importar las tablas del archivo .sql
                conexion = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )
                inicializar_db(conexion)
                return conexion
                
            except Exception as e:
                raise RuntimeError(f"Error crítico al crear e inicializar MySQL: {e}")
        else:
            # Error de servidor apagado (XAMPP) u otro problema
            raise RuntimeError(f"No se pudo conectar a MySQL. Asegúrate de que XAMPP esté encendido: {err}")

def inicializar_db(conn):
    """Lee el archivo unilink.sql y ejecuta su estructura dentro de MySQL."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo de estructura en la ruta: {SCHEMA_PATH}")
        
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    cursor = conn.cursor()
    
    # multi=True permite procesar todo el archivo .sql con múltiples tablas e instrucciones
    resultados = cursor.execute(schema_sql, multi=True)
    
    # Ciclo obligatorio para limpiar el buffer de MySQL y procesar cada comando
    for res in resultados:
        pass
        
    conn.commit()
    cursor.close()
    print(f"-> [Éxito] Estructura relacional de '{SCHEMA_PATH}' cargada correctamente en MySQL.")