from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "database" / "data" / "ventas.db"

SCHEMA_PATH = BASE_DIR / "database" / "unilink.sql"

#ruta de imagenes
ICON_PATH = BASE_DIR / "recursos" / "iconos" / "isologo.ico"
IMAGE_POST = BASE_DIR / "recursos" / "img" / "isologo.png"

ADMIN_IMG = BASE_DIR / "recursos" / "img" / "admin.png"
VENTAS_IMG = BASE_DIR / "recursos" / "img" / "ventas.png"
ALMACEN_IMG = BASE_DIR / "recursos" / "img" / "almacen.png"
