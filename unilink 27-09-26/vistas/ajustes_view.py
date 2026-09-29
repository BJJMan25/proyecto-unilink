import subprocess
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from config import BASE_DIR
from database.conexion import conectar_db


class VistaAjustes(ctk.CTkFrame):
    """Vista de configuración general del sistema para administradores."""

    def __init__(self, parent, usuario=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.usuario = usuario
        self.wrapper = None
        self._crear_schema()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.bind("<Configure>", self._ajustar_responsive)

        self._crear_header()
        self._crear_formularios()
        self.cargar_configuracion()
        self.after(50, self._ajustar_responsive)

    def _ajustar_responsive(self, event=None):
        if self.wrapper is None:
            return
        ancho = max(self.winfo_width(), 1)
        if ancho < 1100:
            self.wrapper.grid_columnconfigure(0, weight=1)
        else:
            self.wrapper.grid_columnconfigure(0, weight=1)

    def _crear_schema(self):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS configuracion_sistema (
                        id_config INT AUTO_INCREMENT PRIMARY KEY,
                        rif_nit VARCHAR(50),
                        nombre_negocio VARCHAR(150),
                        direccion VARCHAR(200),
                        telefono VARCHAR(40),
                        moneda VARCHAR(10) DEFAULT 'PEN',
                        tasa_cambio DECIMAL(10,4) DEFAULT 3.7000,
                        fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.commit()
        except Exception as exc:
            print(f"[Ajustes] Error preparando esquema: {exc}")

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(20, 14))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Ajustes del Sistema",
            text_color="#1A1A1A",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

    def _crear_formularios(self):
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.wrapper = wrapper
        wrapper.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        wrapper.grid_columnconfigure(0, weight=1)

        empresa = ctk.CTkFrame(wrapper, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        empresa.grid(row=0, column=0, sticky="ew", padx=(0, 0), pady=(0, 14))
        empresa.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(empresa, text="Empresa", text_color="#1A1A1A", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        self.entrada_rif = ctk.CTkEntry(empresa, placeholder_text="RIF / NIT", height=38)
        self.entrada_rif.grid(row=1, column=0, sticky="ew", padx=18, pady=6)

        self.entrada_nombre = ctk.CTkEntry(empresa, placeholder_text="Nombre del negocio", height=38)
        self.entrada_nombre.grid(row=2, column=0, sticky="ew", padx=18, pady=6)

        self.entrada_direccion = ctk.CTkEntry(empresa, placeholder_text="Dirección", height=38)
        self.entrada_direccion.grid(row=3, column=0, sticky="ew", padx=18, pady=6)

        self.entrada_telefono = ctk.CTkEntry(empresa, placeholder_text="Teléfono", height=38)
        self.entrada_telefono.grid(row=4, column=0, sticky="ew", padx=18, pady=(6, 14))

        moneda = ctk.CTkFrame(wrapper, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        moneda.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        moneda.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(moneda, text="Moneda y tasa", text_color="#1A1A1A", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        self.select_moneda = ctk.CTkOptionMenu(moneda, values=["PEN", "USD", "VES", "EUR"], width=200)
        self.select_moneda.grid(row=1, column=0, sticky="ew", padx=18, pady=6)

        self.entrada_tasa = ctk.CTkEntry(moneda, placeholder_text="Tasa de cambio del día", height=38)
        self.entrada_tasa.grid(row=2, column=0, sticky="ew", padx=18, pady=(6, 18))

        ctk.CTkButton(
            moneda,
            text="Guardar configuración",
            width=220,
            height=38,
            corner_radius=10,
            fg_color="#2FA572",
            hover_color="#248963",
            command=self.guardar_configuracion
        ).grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))

        base = ctk.CTkFrame(wrapper, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        base.grid(row=2, column=0, sticky="ew")
        base.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(base, text="Base de datos y mantenimiento", text_color="#1A1A1A", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        self.lbl_estado_bd = ctk.CTkLabel(base, text="Conectando a MySQL...", text_color="#2FA572", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_estado_bd.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        ctk.CTkButton(
            base,
            text="Generar respaldo .sql",
            width=220,
            height=38,
            corner_radius=10,
            fg_color="#1F2B2F",
            hover_color="#293B40",
            command=self.generar_respaldo_mysql
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 18))

    def cargar_configuracion(self):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM configuracion_sistema ORDER BY id_config DESC LIMIT 1")
                registro = cursor.fetchone()
                if registro:
                    self.entrada_rif.insert(0, registro.get("rif_nit") or "")
                    self.entrada_nombre.insert(0, registro.get("nombre_negocio") or "")
                    self.entrada_direccion.insert(0, registro.get("direccion") or "")
                    self.entrada_telefono.insert(0, registro.get("telefono") or "")
                    self.select_moneda.set(registro.get("moneda") or "PEN")
                    self.entrada_tasa.insert(0, str(registro.get("tasa_cambio") or "3.7000"))

                try:
                    with conectar_db() as conn_db:
                        conn_db.cursor().execute("SELECT 1")
                    self.lbl_estado_bd.configure(text="Estado: Base de datos conectada", text_color="#2FA572")
                except Exception:
                    self.lbl_estado_bd.configure(text="Estado: MySQL no disponible", text_color="#D95F5F")
        except Exception as exc:
            self.lbl_estado_bd.configure(text=f"Estado: Error de conexión ({exc})", text_color="#D95F5F")

    def guardar_configuracion(self):
        rif = self.entrada_rif.get().strip()
        nombre = self.entrada_nombre.get().strip()
        direccion = self.entrada_direccion.get().strip()
        telefono = self.entrada_telefono.get().strip()
        moneda = self.select_moneda.get().strip()
        tasa = self.entrada_tasa.get().strip()

        if not all([rif, nombre, direccion, telefono, moneda, tasa]):
            messagebox.showwarning("Validación", "Completa todos los campos antes de guardar.")
            return

        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO configuracion_sistema (rif_nit, nombre_negocio, direccion, telefono, moneda, tasa_cambio)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (rif, nombre, direccion, telefono, moneda, float(tasa)),
                )
                conn.commit()
            messagebox.showinfo("Éxito", "Configuración guardada de forma correcta.")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {exc}")

    def generar_respaldo_mysql(self):
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = backup_dir / f"unilink_backup_{fecha}.sql"

        try:
            resultado = subprocess.run(
                ["mysqldump", "-u", "root", "--password=", "unilink"],
                capture_output=True,
                text=True,
                check=False,
            )
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr or "No se pudo generar el respaldo.")
            archivo.write_text(resultado.stdout, encoding="utf-8")
            messagebox.showinfo("Respaldo", f"Respaldo generado correctamente en:\n{archivo}")
        except Exception as exc:
            messagebox.showwarning("Respaldo manual", f"No fue posible generar el respaldo automático con mysqldump: {exc}\n\nSe recomienda ejecutar manualmente el comando desde MySQL Workbench o XAMPP.")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1200x820")
    VistaAjustes(root).pack(fill="both", expand=True)
    root.mainloop()
