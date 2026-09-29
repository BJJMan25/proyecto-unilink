import customtkinter as ctk
from tkinter import ttk, messagebox
from pathlib import Path

from database.conexion import conectar_db


class VistaInventario(ctk.CTkFrame):
    """Vista de inventario y catálogo para roles de encargado o almacén."""

    def __init__(self, parent, usuario=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.usuario = usuario
        self._preparar_esquema()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.bind("<Configure>", self._ajustar_responsive)

        self._crear_header()
        self._crear_kpis()
        self._crear_busqueda()
        self._crear_destacados()
        self._crear_tabla()
        self.cargar_datos()
        self.after(50, self._ajustar_responsive)

    def _ajustar_responsive(self, event=None):
        ancho = max(self.winfo_width(), 1)
        if not hasattr(self, "kpis") or not self.kpis:
            return

        if ancho < 1000:
            self.grid_columnconfigure(0, weight=1)
            for key in self.kpis:
                self.kpis[key].grid_configure(sticky="ew")
        else:
            for key in self.kpis:
                self.kpis[key].grid_configure(sticky="nsew")

    def _preparar_esquema(self):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SHOW COLUMNS FROM productos LIKE 'stock_minimo'")
                if cursor.fetchone() is None:
                    cursor.execute("ALTER TABLE productos ADD COLUMN stock_minimo INT NOT NULL DEFAULT 5 AFTER stock")
                    conn.commit()

                cursor.execute("SHOW TABLES LIKE 'categorias'")
                if cursor.fetchone() is None:
                    cursor.execute("CREATE TABLE categorias (id_categoria INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL)")
                    conn.commit()

                cursor.execute("SELECT COUNT(*) FROM categorias")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO categorias (nombre) VALUES (%s)",
                        [("Bebidas",), ("Lácteos",), ("Abarrotes",), ("Limpieza",), ("Snacks",)]
                    )
                    conn.commit()
        except Exception as exc:
            print(f"[Inventario] Preparación del esquema: {exc}")

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 14))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Gestión de Inventario",
            text_color="#1A1A1A",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            actions,
            text="Nuevo producto",
            width=170,
            height=36,
            corner_radius=10,
            fg_color="#2FA572",
            hover_color="#248963",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._abrir_formulario_producto
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Ajuste de stock",
            width=170,
            height=36,
            corner_radius=10,
            fg_color="#FFFFFF",
            hover_color="#EAF1F3",
            text_color="#1A1A1A",
            border_width=1,
            border_color="#D9E1E5",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._abrir_ajuste_stock
        ).grid(row=0, column=1)

    def _crear_kpis(self):
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpis = {
            "total": self._kpi_card(kpi_frame, "Total Productos", "0", "Productos activos", "#2FA572", 0)[1],
            "critico": self._kpi_card(kpi_frame, "Stock Crítico", "0", "Requieren revisión", "#E0873E", 1)[1],
            "valor": self._kpi_card(kpi_frame, "Valor Inventario", "S/ 0.00", "Costo estimado", "#2FA572", 2)[1],
            "categorias": self._kpi_card(kpi_frame, "Categorías", "0", "Clasificaciones", "#3A8BDA", 3)[1],
        }

    def _kpi_card(self, parent, title, value, subtitle, accent, column):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0 if column == 3 else 10))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=title, text_color="#5E6C74", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        value_label = ctk.CTkLabel(card, text=value, text_color="#1A1A1A", font=ctk.CTkFont(size=24, weight="bold"))
        value_label.grid(row=1, column=0, sticky="w", padx=16)
        ctk.CTkLabel(card, text=subtitle, text_color=accent, font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 16))
        return card, value_label

    def _crear_busqueda(self):
        search = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E7ECEF")
        search.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        search.grid_columnconfigure(0, weight=1)

        self.entry_busqueda = ctk.CTkEntry(
            search,
            placeholder_text="Buscar por nombre, código o categoría",
            height=38,
            fg_color="#F4F6F8",
            border_color="#DCE5E8",
            text_color="#1A1A1A"
        )
        self.entry_busqueda.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar_tabla)

    def _crear_destacados(self):
        destacados = ctk.CTkFrame(self, fg_color="transparent")
        destacados.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
        destacados.grid_columnconfigure((0, 1, 2), weight=1)

        encabezado = ctk.CTkLabel(
            destacados,
            text="Productos destacados",
            text_color="#1A1A1A",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        encabezado.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        productos = sorted(
            self._consultar_productos(),
            key=lambda p: (int(p.get("stock", 0) or 0), float(p.get("precio_venta", 0) or 0)),
            reverse=True,
        )[:3]

        if not productos:
            placeholder = ctk.CTkLabel(
                destacados,
                text="No hay productos disponibles para destacar.",
                text_color="#64748B",
                font=ctk.CTkFont(size=12),
            )
            placeholder.grid(row=1, column=0, columnspan=3, sticky="w", pady=8)
            return

        for idx, producto in enumerate(productos):
            card = ctk.CTkFrame(destacados, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
            card.grid(row=1, column=idx, sticky="nsew", padx=(0 if idx == 0 else 10, 0 if idx == 2 else 10))
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=producto.get("descripcion", "Producto"), text_color="#111827", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 4))
            ctk.CTkLabel(card, text=f"Stock: {producto.get('stock', 0)}", text_color="#475569", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=14, pady=2)
            ctk.CTkLabel(card, text=f"Precio: S/ {float(producto.get('precio_venta', 0) or 0):,.2f}", text_color="#2FA572", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=14, pady=(2, 14))

    def _crear_tabla(self):
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        tabla_frame.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 18))
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "codigo", "descripcion", "categoria", "precio_compra", "precio_venta", "stock", "stock_minimo", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=15)

        encabezados = {
            "id": "ID",
            "codigo": "Código",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "precio_compra": "Compra",
            "precio_venta": "Venta",
            "stock": "Stock",
            "stock_minimo": "Mínimo",
            "estado": "Estado",
        }
        for key, value in encabezados.items():
            self.tree.heading(key, text=value)

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("codigo", width=120, anchor="center")
        self.tree.column("descripcion", width=220)
        self.tree.column("categoria", width=120, anchor="center")
        self.tree.column("precio_compra", width=90, anchor="center")
        self.tree.column("precio_venta", width=90, anchor="center")
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("stock_minimo", width=80, anchor="center")
        self.tree.column("estado", width=110, anchor="center")

        scroll = ctk.CTkScrollbar(tabla_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)

        self.tree.bind("<Double-1>", lambda event: self._editar_producto_seleccionado())

    def _filtrar_tabla(self, event=None):
        termino = self.entry_busqueda.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = self._consultar_productos()
        for producto in productos:
            texto = " ".join([
                str(producto.get("codigo", "")),
                str(producto.get("descripcion", "")),
                str(producto.get("categoria", "")),
            ]).lower()
            if not termino or termino in texto:
                self._agregar_producto_tree(producto)

    def _consultar_productos(self):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """
                    SELECT p.id_producto, p.codigo_barras AS codigo, p.nombre AS descripcion,
                           COALESCE(c.nombre, 'Sin categoría') AS categoria,
                           p.precio_compra, p.precio_venta, p.stock,
                           COALESCE(p.stock_minimo, 5) AS stock_minimo
                    FROM productos p
                    LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
                    ORDER BY p.nombre ASC
                    """
                )
                return cursor.fetchall()
        except Exception as exc:
            print(f"[Inventario] Error consultando productos: {exc}")
            return []

    def cargar_datos(self):
        self._filtrar_tabla()
        self._refrescar_kpis()

    def _refrescar_kpis(self):
        productos = self._consultar_productos()
        total = len(productos)
        criticos = sum(1 for p in productos if int(p.get("stock", 0)) <= int(p.get("stock_minimo", 5)))
        valor = sum(float(p.get("precio_compra", 0) or 0) * int(p.get("stock", 0)) for p in productos)
        categorias = 0
        try:
            with conectar_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM categorias")
                categorias = cursor.fetchone()[0]
        except Exception:
            categorias = 0

        self.kpis["total"].configure(text=str(total))
        self.kpis["critico"].configure(text=str(criticos))
        self.kpis["valor"].configure(text=f"S/ {valor:,.2f}")
        self.kpis["categorias"].configure(text=str(categorias))

    def _agregar_producto_tree(self, producto):
        stock = int(producto.get("stock", 0) or 0)
        minimo = int(producto.get("stock_minimo", 5) or 5)
        estado = "Stock OK" if stock > minimo else "Stock Bajo"
        color = "#2FA572" if stock > minimo else "#E0873E"

        self.tree.insert(
            "",
            "end",
            values=(
                producto.get("id_producto", ""),
                producto.get("codigo", ""),
                producto.get("descripcion", ""),
                producto.get("categoria", ""),
                f"S/ {float(producto.get('precio_compra', 0) or 0):,.2f}",
                f"S/ {float(producto.get('precio_venta', 0) or 0):,.2f}",
                stock,
                minimo,
                estado,
            )
        )
        item_id = self.tree.get_children()[-1]
        self.tree.item(item_id, tags=(estado,))
        self.tree.tag_configure("Stock OK", foreground="#2FA572")
        self.tree.tag_configure("Stock Bajo", foreground="#E0873E")

    def _abrir_formulario_producto(self, producto_id=None):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registrar producto" if producto_id is None else "Editar producto")
        dialogo.geometry("520x560")
        dialogo.minsize(480, 520)
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.configure(fg_color="#F4F6F8")

        frame = ctk.CTkFrame(dialogo, fg_color="#FFFFFF", corner_radius=18)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Datos del producto", text_color="#1A1A1A", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 12))

        campos = {}
        campos["codigo"] = ctk.CTkEntry(frame, placeholder_text="Código de barras", height=38)
        campos["codigo"].grid(row=1, column=0, padx=18, pady=6, sticky="ew")

        campos["descripcion"] = ctk.CTkEntry(frame, placeholder_text="Descripción / nombre del producto", height=38)
        campos["descripcion"].grid(row=2, column=0, padx=18, pady=6, sticky="ew")

        campos["categoria"] = ctk.CTkOptionMenu(frame, values=["Bebidas", "Lácteos", "Abarrotes", "Limpieza", "Snacks"])
        campos["categoria"].grid(row=3, column=0, padx=18, pady=6, sticky="ew")

        campos["precio_compra"] = ctk.CTkEntry(frame, placeholder_text="Precio compra", height=38)
        campos["precio_compra"].grid(row=4, column=0, padx=18, pady=6, sticky="ew")

        campos["precio_venta"] = ctk.CTkEntry(frame, placeholder_text="Precio venta", height=38)
        campos["precio_venta"].grid(row=5, column=0, padx=18, pady=6, sticky="ew")

        campos["stock"] = ctk.CTkEntry(frame, placeholder_text="Stock actual", height=38)
        campos["stock"].grid(row=6, column=0, padx=18, pady=6, sticky="ew")

        campos["stock_minimo"] = ctk.CTkEntry(frame, placeholder_text="Stock mínimo", height=38)
        campos["stock_minimo"].grid(row=7, column=0, padx=18, pady=6, sticky="ew")

        if producto_id is not None:
            producto = self._obtener_producto_por_id(producto_id)
            if producto:
                campos["codigo"].insert(0, producto.get("codigo", ""))
                campos["descripcion"].insert(0, producto.get("descripcion", ""))
                campos["categoria"].set(producto.get("categoria", "Bebidas"))
                campos["precio_compra"].insert(0, str(producto.get("precio_compra", 0)))
                campos["precio_venta"].insert(0, str(producto.get("precio_venta", 0)))
                campos["stock"].insert(0, str(producto.get("stock", 0)))
                campos["stock_minimo"].insert(0, str(producto.get("stock_minimo", 5)))

        def guardar():
            datos = {k: v.get().strip() for k, v in campos.items()}
            if not all(datos.values()):
                messagebox.showwarning("Validación", "Completa todos los campos del producto.")
                return
            try:
                with conectar_db() as conn:
                    cursor = conn.cursor()
                    categoria = datos["categoria"]
                    cursor.execute("SELECT id_categoria FROM categorias WHERE nombre = %s", (categoria,))
                    categoria_row = cursor.fetchone()
                    if categoria_row is None:
                        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (categoria,))
                        categoria_id = cursor.lastrowid
                    else:
                        categoria_id = categoria_row[0]

                    if producto_id is None:
                        cursor.execute(
                            """
                            INSERT INTO productos (codigo_barras, nombre, descripcion, precio_compra, precio_venta,
                                                  stock, stock_minimo, id_categoria)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                datos["codigo"],
                                datos["descripcion"],
                                datos["descripcion"],
                                float(datos["precio_compra"]),
                                float(datos["precio_venta"]),
                                int(datos["stock"]),
                                int(datos["stock_minimo"]),
                                categoria_id,
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            UPDATE productos SET codigo_barras=%s, nombre=%s, descripcion=%s, precio_compra=%s,
                                                precio_venta=%s, stock=%s, stock_minimo=%s, id_categoria=%s
                            WHERE id_producto=%s
                            """,
                            (
                                datos["codigo"],
                                datos["descripcion"],
                                datos["descripcion"],
                                float(datos["precio_compra"]),
                                float(datos["precio_venta"]),
                                int(datos["stock"]),
                                int(datos["stock_minimo"]),
                                categoria_id,
                                producto_id,
                            ),
                        )
                    conn.commit()
                    messagebox.showinfo("Éxito", "Producto guardado correctamente.")
                    dialogo.destroy()
                    self.cargar_datos()
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo guardar el producto: {exc}")

        ctk.CTkButton(frame, text="Guardar", width=200, height=38, fg_color="#2FA572", hover_color="#248963", command=guardar).grid(row=8, column=0, padx=18, pady=(14, 14))

    def _editar_producto_seleccionado(self):
        item = self.tree.selection()
        if not item:
            return
        producto_id = self.tree.item(item[0], "values")[0]
        self._abrir_formulario_producto(producto_id)

    def _obtener_producto_por_id(self, producto_id):
        try:
            with conectar_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """
                    SELECT p.id_producto, p.codigo_barras AS codigo, p.nombre AS descripcion,
                           COALESCE(c.nombre, 'Sin categoría') AS categoria,
                           p.precio_compra, p.precio_venta, p.stock,
                           COALESCE(p.stock_minimo, 5) AS stock_minimo
                    FROM productos p
                    LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
                    WHERE p.id_producto = %s
                    """,
                    (producto_id,),
                )
                return cursor.fetchone()
        except Exception:
            return None

    def _abrir_ajuste_stock(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Seleccione un producto para registrar un ajuste.")
            return

        producto_id = self.tree.item(seleccion[0], "values")[0]
        producto = self._obtener_producto_por_id(producto_id)
        if not producto:
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Ajuste de mercadería")
        dialogo.geometry("460x320")
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.configure(fg_color="#F4F6F8")

        frame = ctk.CTkFrame(dialogo, fg_color="#FFFFFF", corner_radius=18)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=producto["descripcion"], text_color="#1A1A1A", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 4), sticky="w")
        ctk.CTkLabel(frame, text=f"Stock actual: {producto['stock']} | Mínimo: {producto['stock_minimo']}", text_color="#5E6C74").grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")

        cant = ctk.CTkEntry(frame, placeholder_text="Cantidad a ingresar o ajustar", height=38)
        cant.grid(row=2, column=0, padx=18, sticky="ew")

        motivo = ctk.CTkEntry(frame, placeholder_text="Motivo del ajuste", height=38)
        motivo.grid(row=3, column=0, padx=18, pady=(8, 14), sticky="ew")

        def registrar():
            try:
                cantidad = int(cant.get().strip())
                if cantidad <= 0:
                    raise ValueError()
                descripcion = motivo.get().strip() or "Ajuste de inventario"
                with conectar_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, descripcion) VALUES (%s, %s, %s, %s)",
                        (producto_id, "Entrada", cantidad, descripcion),
                    )
                    cursor.execute(
                        "UPDATE productos SET stock = stock + %s WHERE id_producto = %s",
                        (cantidad, producto_id),
                    )
                    conn.commit()
                messagebox.showinfo("Éxito", "Ajuste de inventario registrado.")
                dialogo.destroy()
                self.cargar_datos()
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo registrar el ajuste: {exc}")

        ctk.CTkButton(frame, text="Registrar ajuste", width=220, height=38, fg_color="#2FA572", hover_color="#248963", command=registrar).grid(row=4, column=0, padx=18, pady=(0, 16))


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1400x800")
    VistaInventario(root).pack(fill="both", expand=True)
    root.mainloop()
