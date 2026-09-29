import hashlib
from database.conexion import conectar_db

def reparar_administrador():
    usuario_admin = "admin"
    nueva_contrasena = "admin123"
    
    # 1. Generamos el hash exactamente como lo hace tu aplicación
    hash_correcto = hashlib.sha256(nueva_contrasena.encode('utf-8')).hexdigest()
    
    print(f"[INFO] Hash generado por Python para '{nueva_contrasena}':")
    print(f"👉 {hash_correcto}\n")

    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            
            # 2. Limpiamos cualquier residuo previo del usuario admin
            cursor.execute("DELETE FROM usuarios WHERE nombre_usuario = %s", (usuario_admin,))
            
            # 3. Insertamos el usuario con el hash nativo de Python
            query = """
                INSERT INTO usuarios (nombre_completo, nombre_usuario, contrasena, rol_id, activo)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, ("Administrador Sistema", usuario_admin, hash_correcto, 1, 1))
            conn.commit()
            
            print("======================================================")
            print("🎉 ¡Usuario 'admin' restablecido con éxito en MySQL!")
            print(f"👤 Usuario: {usuario_admin}")
            print(f"🔑 Contraseña: {nueva_contrasena}")
            print("======================================================")
            print("Ya puedes borrar este archivo y ejecutar main.py para entrar.")

    except Exception as e:
        print(f"[❌ ERROR AL CONECTAR O ACTUALIZAR LA DB]: {str(e)}")

if __name__ == "__main__":
    reparar_administrador()