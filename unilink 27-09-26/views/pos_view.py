import customtkinter as ctk
from tkinter import ttk, messagebox


class POSView(ctk.CTkFrame):
    """Vista de terminal de venta / facturación con carrito y cobro final."""

    PAYMENT_OPTIONS = ["Efectivo", "Transferencia / Pago Móvil", "Punto de Venta", "Crédito"]

    def __init__(self, parent, products=None, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.products = products or []
        self.cart = []
        self.current_total = 0.0

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_products_panel()
        self._build_cart_panel()
        self.load_demo_products()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Terminal de Venta",
            text_color="#111827",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

    def _build_products_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#E7ECEF", corner_radius=18)
        panel.grid(row=1, column=0, sticky="nsew", padx=(22, 10), pady=(0, 18))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        search_row = ctk.CTkFrame(panel, fg_color="transparent")
        search_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        search_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Buscar por código o nombre",
            height=38,
            fg_color="#F4F6F8",
            border_color="#D9E1E5",
            text_color="#111827",
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            search_row,
            text="Agregar",
            width=110,
            height=38,
            corner_radius=10,
            fg_color="#2FA572",
            hover_color="#248963",
            text_color="#FFFFFF",
            command=self.add_product_from_search,
        ).grid(row=0, column=1)

        self.product_tree = ttk.Treeview(panel, columns=("id", "codigo", "nombre", "precio", "stock"), show="headings", height=15)
        for key, label in {"id": "ID", "codigo": "Código", "nombre": "Producto", "precio": "Precio", "stock": "Stock"}.items():
            self.product_tree.heading(key, text=label)

        self.product_tree.column("id", width=60, anchor="center")
        self.product_tree.column("codigo", width=110, anchor="center")
        self.product_tree.column("nombre", width=220, anchor="w")
        self.product_tree.column("precio", width=100, anchor="center")
        self.product_tree.column("stock", width=80, anchor="center")

        y_scroll = ctk.CTkScrollbar(panel, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=y_scroll.set)
        self.product_tree.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0, 16))
        y_scroll.grid(row=1, column=1, sticky="ns", padx=(0, 16), pady=(0, 16))
        self.product_tree.bind("<Double-1>", lambda event: self.add_selected_product())

        self.panel_productos = panel

    def _build_cart_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#E7ECEF", corner_radius=18)
        panel.grid(row=1, column=1, sticky="nsew", padx=(10, 22), pady=(0, 18))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Carrito", text_color="#111827", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

        cols = ("nombre", "cantidad", "precio", "subtotal")
        self.cart_tree = ttk.Treeview(panel, columns=cols, show="headings", height=10)
        for key, label in {"nombre": "Producto", "cantidad": "Cant.", "precio": "Precio", "subtotal": "Subtotal"}.items():
            self.cart_tree.heading(key, text=label)
        self.cart_tree.column("nombre", width=180)
        self.cart_tree.column("cantidad", width=60, anchor="center")
        self.cart_tree.column("precio", width=90, anchor="center")
        self.cart_tree.column("subtotal", width=110, anchor="center")
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=16)

        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 8))
        actions.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(actions, text="Quitar", width=120, height=34, fg_color="#E11D48", hover_color="#BE123C", command=self.remove_selected_item).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(actions, text="Limpiar", width=120, height=34, fg_color="#94A3B8", hover_color="#64748B", command=self.clear_cart).grid(row=0, column=1, sticky="ew")

        totals = ctk.CTkFrame(panel, fg_color="#F4F6F8", corner_radius=12)
        totals.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 10))
        totals.grid_columnconfigure(0, weight=1)

        self.subtotal_label = ctk.CTkLabel(totals, text="Subtotal: S/ 0.00", text_color="#111827", font=ctk.CTkFont(size=13, weight="bold"))
        self.subtotal_label.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.iva_label = ctk.CTkLabel(totals, text="IVA: S/ 0.00", text_color="#111827", font=ctk.CTkFont(size=13, weight="bold"))
        self.iva_label.grid(row=1, column=0, sticky="w", padx=12, pady=4)

        self.total_label = ctk.CTkLabel(totals, text="TOTAL: S/ 0.00", text_color="#2FA572", font=ctk.CTkFont(size=22, weight="bold"))
        self.total_label.grid(row=2, column=0, sticky="w", padx=12, pady=(6, 12))

        cash = ctk.CTkFrame(panel, fg_color="transparent")
        cash.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 10))
        cash.grid_columnconfigure(0, weight=1)
        self.received_entry = ctk.CTkEntry(cash, placeholder_text="Efectivo recibido", height=36, fg_color="#F4F6F8", border_color="#D9E1E5")
        self.received_entry.grid(row=0, column=0, sticky="ew")
        self.received_entry.bind("<KeyRelease>", self.update_change)

        self.change_label = ctk.CTkLabel(panel, text="Cambio: S/ 0.00", text_color="#111827", font=ctk.CTkFont(size=14, weight="bold"))
        self.change_label.grid(row=5, column=0, sticky="w", padx=16, pady=(0, 8))

        ctk.CTkButton(
            panel,
            text="Emitir Factura / Cobro Final",
            height=42,
            corner_radius=12,
            fg_color="#2FA572",
            hover_color="#248963",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.open_payment_modal,
        ).grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 18))

        self.panel_carrito = panel

    def load_demo_products(self):
        self.products = [
            {"id": 1, "codigo": "A1001", "nombre": "Gaseosa 500ml", "precio": 4.5, "stock": 18},
            {"id": 2, "codigo": "B2002", "nombre": "Arroz 1kg", "precio": 8.2, "stock": 12},
            {"id": 3, "codigo": "C3003", "nombre": "Yogurt Natural", "precio": 5.5, "stock": 21},
            {"id": 4, "codigo": "D4004", "nombre": "Jabón Líquido", "precio": 9.0, "stock": 9},
            {"id": 5, "codigo": "E5005", "nombre": "Galletas Clásicas", "precio": 3.2, "stock": 25},
        ]
        self.render_products()

    def render_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        for product in self.products:
            self.product_tree.insert(
                "",
                "end",
                values=(product["id"], product["codigo"], product["nombre"], f"S/ {product['precio']:.2f}", product["stock"]),
            )

    def add_product_from_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Búsqueda", "Escribe un código o nombre para buscar.")
            return

        match = next((p for p in self.products if p["codigo"].lower() == keyword.lower() or p["nombre"].lower().startswith(keyword.lower())), None)
        if match is None:
            messagebox.showwarning("Sin coincidencias", "No se encontró el producto buscado.")
            return

        self.add_to_cart(match)

    def add_selected_product(self):
        selection = self.product_tree.selection()
        if not selection:
            return
        product_id = self.product_tree.item(selection[0], "values")[0]
        product = next((p for p in self.products if p["id"] == product_id), None)
        if product:
            self.add_to_cart(product)

    def add_to_cart(self, product):
        for item in self.cart:
            if item["id"] == product["id"]:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                self.refresh_cart()
                return

        self.cart.append(
            {
                "id": product["id"],
                "nombre": product["nombre"],
                "cantidad": 1,
                "precio": float(product["precio"]),
                "subtotal": float(product["precio"]),
            }
        )
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        subtotal = 0.0
        for item in self.cart:
            subtotal += item["subtotal"]
            self.cart_tree.insert("", "end", values=(item["nombre"], item["cantidad"], f"S/ {item['precio']:.2f}", f"S/ {item['subtotal']:.2f}"))

        iva = subtotal * 0.18
        total = subtotal + iva
        self.current_total = total
        self.subtotal_label.configure(text=f"Subtotal: S/ {subtotal:.2f}")
        self.iva_label.configure(text=f"IVA (18%): S/ {iva:.2f}")
        self.total_label.configure(text=f"TOTAL: S/ {total:.2f}")
        self.update_change()

    def update_change(self, event=None):
        try:
            received = float(self.received_entry.get().strip() or 0)
        except ValueError:
            received = 0.0
        change = max(0.0, received - self.current_total)
        self.change_label.configure(text=f"Cambio: S/ {change:.2f}")

    def remove_selected_item(self):
        selection = self.cart_tree.selection()
        if not selection:
            return

        index = self.cart_tree.index(selection[0])
        self.cart.pop(index)
        self.refresh_cart()

    def clear_cart(self):
        self.cart.clear()
        self.received_entry.delete(0, "end")
        self.current_total = 0.0
        self.refresh_cart()

    def open_payment_modal(self):
        if not self.cart:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto antes de facturar.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Emitir Factura / Cobro Final")
        modal.geometry("860x620")
        modal.minsize(760, 520)
        modal.grab_set()
        modal.transient(self)
        modal.configure(fg_color="#F4F6F8")

        main = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=18)
        main.pack(fill="both", expand=True, padx=18, pady=18)
        main.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(main, text="Cobro Final", text_color="#111827", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 12))

        left = ctk.CTkFrame(main, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0", corner_radius=16)
        left.grid(row=1, column=0, padx=(18, 10), pady=(0, 18), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Cliente", text_color="#111827", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        rif = ctk.CTkEntry(left, placeholder_text="ID Fiscal / RIF", height=38)
        rif.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        nombre = ctk.CTkEntry(left, placeholder_text="Nombre / Razón Social", height=38)
        nombre.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        direccion = ctk.CTkEntry(left, placeholder_text="Dirección Fiscal", height=38)
        direccion.grid(row=3, column=0, padx=16, pady=6, sticky="ew")

        right = ctk.CTkFrame(main, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0", corner_radius=16)
        right.grid(row=1, column=1, padx=(10, 18), pady=(0, 18), sticky="nsew")
        right.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(right, text="Métodos de Pago", text_color="#111827", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 14))

        payment_var = ctk.StringVar(value="Efectivo")
        payment_buttons = []
        for idx, label in enumerate(self.PAYMENT_OPTIONS):
            btn = ctk.CTkButton(
                right,
                text=label,
                width=150,
                height=42,
                corner_radius=10,
                fg_color="#D9E1E5" if label != "Efectivo" else "#2FA572",
                hover_color="#CBD5E1",
                text_color="#111827" if label != "Efectivo" else "#FFFFFF",
                command=lambda value=label: payment_var.set(value),
            )
            row = 1 + (idx // 2)
            col = idx % 2
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            payment_buttons.append(btn)

        ctk.CTkLabel(right, text="Monto recibido", text_color="#374151", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8))
        received = ctk.CTkEntry(right, placeholder_text="0.00", height=38)
        received.grid(row=4, column=0, columnspan=2, padx=16, sticky="ew")

        summary = ctk.CTkFrame(right, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E7ECEF")
        summary.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 10))
        summary.grid_columnconfigure(0, weight=1)

        total_value = ctk.CTkLabel(summary, text=f"Total a pagar: S/ {self.current_total:.2f}", text_color="#111827", font=ctk.CTkFont(size=13, weight="bold"))
        total_value.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        def sync_change(event=None):
            try:
                ingreso = float(received.get().strip() or 0)
            except ValueError:
                ingreso = 0.0
            cambio = max(0.0, ingreso - self.current_total)
            total_value.configure(text=f"Total a pagar: S/ {self.current_total:.2f}")
            summary_change.configure(text=f"Cambio: S/ {cambio:.2f}")

        summary_change = ctk.CTkLabel(summary, text="Cambio: S/ 0.00", text_color="#2FA572", font=ctk.CTkFont(size=13, weight="bold"))
        summary_change.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
        received.bind("<KeyRelease>", sync_change)

        def finalize():
            try:
                recibido = float(received.get().strip() or 0)
            except ValueError:
                messagebox.showerror("Error", "El monto recibido es inválido.")
                return

            if recibido < self.current_total:
                messagebox.showerror("Cobro insuficiente", "El monto recibido debe ser mayor o igual al total.")
                return

            cambio = recibido - self.current_total
            messagebox.showinfo("Factura emitida", f"Factura registrada correctamente. Cambio: S/ {cambio:.2f}")
            modal.destroy()
            self.clear_cart()

        footer = ctk.CTkFrame(main, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=2, sticky="e", padx=18, pady=(0, 18))
        ctk.CTkButton(footer, text="Cancelar", width=120, height=38, fg_color="#64748B", hover_color="#475569", command=modal.destroy).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(footer, text="Confirmar Factura", width=200, height=38, fg_color="#2FA572", hover_color="#248963", command=finalize).grid(row=0, column=1)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1360x820")
    POSView(root).pack(fill="both", expand=True)
    root.mainloop()
