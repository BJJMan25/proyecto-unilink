import customtkinter as ctk
from tkinter import ttk, messagebox

from database.conexion import conectar_db


class VistaVentas(ctk.CTkFrame):
    """Vista de punto de venta y facturación rápida."""

    def __init__(self, parent, usuario=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.usuario = usuario
        self.carrito = []
        self.metodo_pago = "Efectivo"
        self.catalogo_panel = None
        self.ticket_panel = None

        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        self.bind("<Configure>", self._ajustar_responsive)

        self._crear_header()
        self._crear_catalogo()
        self._crear_ticket()
        self._cargar_catalogo()
        self.after(50, self._ajustar_responsive)

    def _ajustar_responsive(self, event=None):
        if self.catalogo_panel is None or self.ticket_panel is None:
            return

        ancho = max(self.winfo_width(), 1)
        if ancho < 1200:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.catalogo_panel.grid(row=0, column=0, sticky="nsew", padx=(18, 10), pady=(0, 10))
            self.ticket_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 18))
        else:
            self.grid_columnconfigure(0, weight=6)
            self.grid_columnconfigure(1, weight=4)
            self.catalogo_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 18))
            self.ticket_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Terminal de Venta",
            text_color="#1A1A1A",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

    def _crear_catalogo(self):
        panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        self.catalogo_panel = panel
        panel.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 18))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        search = ctk.CTkFrame(panel, fg_color="transparent")
        search.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        search.grid_columnconfigure(0, weight=1)

        self.entry_busqueda = ctk.CTkEntry(
            search,
            placeholder_text="Buscar producto o ingresar código",
            height=38,
            fg_color="#F4F6F8",
            border_color="#DDE7EC"
        )
        self.entry_busqueda.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_busqueda.bind("<Return>", lambda event: self._agregar_por_codigo())

        ctk.CTkButton(
            search,
            text="Agregar",
            width=110,
            height=38,
            fg_color="#2FA572",
            hover_color="#248963",
            command=self._agregar_por_codigo
        ).grid(row=0, column=1)

        cols = ("id", "codigo", "nombre", "precio", "stock")
        self.tree_productos = ttk.Treeview(panel, columns=cols, show="headings", height=16)
        for key, value in {"id": "ID", "codigo": "Código", "nombre": "Producto", "precio": "Precio", "stock": "Stock"}.items():
            self.tree_productos.heading(key, text=value)
        self.tree_productos.column("id", width=40, anchor="center")
        self.tree_productos.column("codigo", width=90, anchor="center")
        self.tree_productos.column("nombre", width=220)
        self.tree_productos.column("precio", width=80, anchor="center")
        self.tree_productos.column("stock", width=70, anchor="center")

        scroll = ctk.CTkScrollbar(panel, command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scroll.set)
        self.tree_productos.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0, 16))
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 16), pady=(0, 16))
        self.tree_productos.bind("<Double-1>", lambda event: self._agregar_producto_seleccionado())

    def _crear_ticket(self):
        panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        self.ticket_panel = panel
        panel.grid(row=1, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Carrito", text_color="#1A1A1A", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        cols = ("nombre", "cantidad", "precio", "subtotal")
        self.tree_carrito = ttk.Treeview(panel, columns=cols, show="headings", height=10)
        for key, value in {"nombre": "Producto", "cantidad": "Cant.", "precio": "Precio", "subtotal": "Subtotal"}.items():
            self.tree_carrito.heading(key, text=value)
        self.tree_carrito.column("nombre", width=170)
        self.tree_carrito.column("cantidad", width=60, anchor="center")
        self.tree_carrito.column("precio", width=80, anchor="center")
        self.tree_carrito.column("subtotal", width=90, anchor="center")
        self.tree_carrito.grid(row=1, column=0, sticky="nsew", padx=18)

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(10, 6))
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="Quitar", width=100, height=34, fg_color="#D95F5F", hover_color="#B54D4D", command=self._quitar_producto).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(btn_row, text="Limpiar", width=100, height=34, fg_color="#D9E1E5", hover_color="#C9D5DB", text_color="#1A1A1A", command=self._limpiar_carrito).grid(row=0, column=1, sticky="ew")

        totales = ctk.CTkFrame(panel, fg_color="#F4F6F8", corner_radius=12)
        totales.grid(row=3, column=0, sticky="ew", padx=18, pady=(10, 10))
        totales.grid_columnconfigure(0, weight=1)

        self.lbl_subtotal = ctk.CTkLabel(totales, text="Subtotal: S/ 0.00", text_color="#1A1A1A", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_subtotal.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.lbl_iva = ctk.CTkLabel(totales, text="IGV (18%): S/ 0.00", text_color="#1A1A1A", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_iva.grid(row=1, column=0, sticky="w", padx=12, pady=4)

        self.lbl_total = ctk.CTkLabel(totales, text="TOTAL: S/ 0.00", text_color="#2FA572", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_total.grid(row=2, column=0, sticky="w", padx=12, pady=(6, 12))

        pago = ctk.CTkFrame(panel, fg_color="transparent")
        pago.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 8))
        pago.grid_columnconfigure((0, 1, 2), weight=1)

        self.metodos = {
            "Efectivo": ctk.CTkButton(pago, text="Efectivo", height=32, fg_color="#2FA572", hover_color="#248963", command=lambda: self._seleccionar_metodo("Efectivo")),
            "Tarjeta": ctk.CTkButton(pago, text="Tarjeta", height=32, fg_color="#D9E1E5", hover_color="#CBD7DD", text_color="#1A1A1A", command=lambda: self._seleccionar_metodo("Tarjeta")),
            "Pago Móvil": ctk.CTkButton(pago, text="Pago Móvil", height=32, fg_color="#D9E1E5", hover_color="#CBD7DD", text_color="#1A1A1A", command=lambda: self._seleccionar_metodo("Pago Móvil")),
        }

        for idx, boton in enumerate(self.metodos.values()):
            boton.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 6, 0))

        self.entry_pago = ctk.CTkEntry(panel, placeholder_text="Monto recibido", height=36)
        self.entry_pago.grid(row=5, column=0, padx=18, pady=(6, 8), sticky="ew")
        self.entry_pago.bind("<KeyRelease>", lambda event: self._actualizar_totales())

        self.lbl_vuelto = ctk.CTkLabel(panel, text="Cambio: S/ 0.00", text_color="#1A1A1A", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_vuelto.grid(row=6, column=0, sticky="w", padx=18, pady=(0, 12))

        ctk.CTkButton(
            panel,
            text="Procesar y emitir factura",
            height=42,
            corner_radius=12,
            fg_color="#2FA572",
            hover_color="#248963",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._procesar_venta
        ).grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 18))

    def _seleccionar_metodo(self, metodo):
        self.metodo_pago = metodo
        for nombre, boton in self.metodos.items():
            if nombre == metodo:
                boton.configure(fg_color="#2FA572", hover_color="#248963", text_color="#FFFFFF")
            else:
                boton.configure(fg_color="#D9E1E5", hover_color="#CBD7DD", text_color="#1A1A1A")

    def _cargar_catalogo(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id_producto, codigo_barras, nombre, precio_venta, stock FROM productos WHERE stock > 0 ORDER BY nombre ASC")
                for producto in cursor.fetchall():
                    self.tree_productos.insert("", "end", values=(producto["id_producto"], producto["codigo_barras"], producto["nombre"], f"S/ {float(producto['precio_venta']):,.2f}", producto["stock"]))
        except Exception as exc:
            print(f"[Ventas] Error cargando catálogo: {exc}")

    def _agregar_producto_seleccionado(self):
        seleccion = self.tree_productos.selection()
        if not seleccion:
            return
        valores = self.tree_productos.item(seleccion[0], "values")
        self._agregar_producto_por_id(valores[0], 1)

    def _agregar_por_codigo(self):
        codigo = self.entry_busqueda.get().strip()
        if not codigo:
            messagebox.showwarning("Búsqueda", "Ingrese un código de barras o texto de búsqueda.")
            return
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id_producto, codigo_barras, nombre, precio_venta, stock FROM productos WHERE codigo_barras = %s AND stock > 0", (codigo,))
                producto = cursor.fetchone()
                if producto is None:
                    cursor.execute("SELECT id_producto, codigo_barras, nombre, precio_venta, stock FROM productos WHERE LOWER(nombre) LIKE %s AND stock > 0 LIMIT 1", (f"%{codigo.lower()}%",))
                    producto = cursor.fetchone()
                if producto is None:
                    messagebox.showwarning("Sin coincidencias", "No se encontró un producto con esos datos.")
                    return
                self._agregar_producto_por_id(producto["id_producto"], 1)
                self.entry_busqueda.delete(0, "end")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo buscar el producto: {exc}")

    def _agregar_producto_por_id(self, producto_id, cantidad):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id_producto, codigo_barras, nombre, precio_venta, stock FROM productos WHERE id_producto = %s", (producto_id,))
                producto = cursor.fetchone()
                if not producto:
                    return
                if producto["stock"] <= 0:
                    messagebox.showwarning("Stock", "Este producto no tiene stock disponible.")
                    return
                for item in self.carrito:
                    if item["id_producto"] == producto_id:
                        item["cantidad"] += cantidad
                        item["subtotal"] = float(item["precio"]) * item["cantidad"]
                        self._actualizar_totales()
                        return
                self.carrito.append({
                    "id_producto": producto["id_producto"],
                    "nombre": producto["nombre"],
                    "cantidad": cantidad,
                    "precio": float(producto["precio_venta"]),
                    "subtotal": float(producto["precio_venta"]) * cantidad,
                })
                self._actualizar_carrito()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {exc}")

    def _actualizar_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        for item in self.carrito:
            self.tree_carrito.insert("", "end", values=(item["nombre"], item["cantidad"], f"S/ {item['precio']:.2f}", f"S/ {item['subtotal']:.2f}"))
        self._actualizar_totales()

    def _actualizar_totales(self):
        subtotal = sum(item["subtotal"] for item in self.carrito)
        iva = subtotal * 0.18
        total = subtotal + iva
        self.lbl_subtotal.configure(text=f"Subtotal: S/ {subtotal:,.2f}")
        self.lbl_iva.configure(text=f"IGV (18%): S/ {iva:,.2f}")
        self.lbl_total.configure(text=f"TOTAL: S/ {total:,.2f}")

        try:
            pago = float(self.entry_pago.get().strip() or 0)
            cambio = max(0, pago - total)
            self.lbl_vuelto.configure(text=f"Cambio: S/ {cambio:,.2f}")
        except ValueError:
            self.lbl_vuelto.configure(text="Cambio: S/ 0.00")

    def _quitar_producto(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            return
        index = self.tree_carrito.index(seleccion[0])
        self.carrito.pop(index)
        self._actualizar_carrito()

    def _limpiar_carrito(self):
        self.carrito.clear()
        self._actualizar_carrito()

    def _procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Debe agregar productos antes de procesar la venta.")
            return

        try:
            subtotal = sum(item["subtotal"] for item in self.carrito)
            total = subtotal * 1.18
            monto_recibido = float(self.entry_pago.get().strip() or 0)
            if monto_recibido < total:
                messagebox.showwarning("Cobro insuficiente", "El monto recibido es menor al total de la venta.")
                return

            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ventas (fecha, total, metodo_pago, estado) VALUES (NOW(), %s, %s, 'completada')",
                    (round(total, 2), self.metodo_pago),
                )
                venta_id = cursor.lastrowid
                for item in self.carrito:
                    cursor.execute(
                        "INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        (venta_id, item["id_producto"], item["cantidad"], item["precio"], item["subtotal"]),
                    )
                    cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s", (item["cantidad"], item["id_producto"]))
                conn.commit()

            messagebox.showinfo("Venta registrada", f"Factura emitida correctamente. Total: S/ {total:,.2f}")
            self.carrito.clear()
            self.entry_pago.delete(0, "end")
            self._actualizar_carrito()
            self._cargar_catalogo()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo procesar la venta: {exc}")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1400x850")
    VistaVentas(root).pack(fill="both", expand=True)
    root.mainloop()
