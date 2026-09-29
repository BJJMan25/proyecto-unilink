import os
import customtkinter as ctk
from tkinter import ttk, messagebox


class VentaView(ctk.CTkFrame):
    def __init__(self, parent, venta_controller):
        super().__init__(parent, fg_color="transparent")

        self.venta_controller = venta_controller
        self.producto_temp = None
        self.panel_productos = None
        self.panel_carrito = None

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.bind("<Configure>", self._ajustar_layout)
        self._crear_header()

        try:
            from ..assets.styles.estilos import estilizar_tabla
            estilizar_tabla()
        except (ModuleNotFoundError, ImportError):
            try:
                from ..recursos.styles.estilos import estilizar_tabla
                estilizar_tabla()
            except (ModuleNotFoundError, ImportError):
                print("[ADVERTENCIA] No se encontró el módulo de estilos en la raíz. Renderizando Treeview estándar.")

        self._crear_panel_productos()
        self._crear_panel_carrito()
        self.after(50, self._ajustar_layout)

    def _ajustar_layout(self, event=None):
        if self.panel_productos is None or self.panel_carrito is None:
            return

        ancho = max(self.winfo_width(), 1)
        if ancho < 1100:
            self.panel_productos.grid(row=1, column=0, sticky="nsew", padx=(20, 8), pady=(0, 12))
            self.panel_carrito.grid(row=2, column=0, sticky="nsew", padx=(20, 8), pady=(0, 12))
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
        else:
            self.panel_productos.grid(row=1, column=0, sticky="nsew", padx=(20, 8), pady=(0, 12))
            self.panel_carrito.grid(row=1, column=1, sticky="nsew", padx=(8, 20), pady=(0, 12))

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Terminal de Venta",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")


    def _crear_panel_productos(self):
        self.panel_productos = ctk.CTkFrame(self)
        self.panel_productos.grid(row=1, column=0, sticky="nsew", padx=(20, 8), pady=(0, 12))
        self.panel_productos.grid_columnconfigure(0, weight=1)
        self.panel_productos.grid_rowconfigure(1, weight=1)

        search_frame = ctk.CTkFrame(self.panel_productos, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        search_frame.grid_columnconfigure(0, weight=1)

        self.entry_codigo = ctk.CTkEntry(search_frame, placeholder_text="Código de barras", height=34)
        self.entry_codigo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entry_codigo.bind("<Return>", lambda e: self._buscar_y_agregar())

        ctk.CTkButton(search_frame, text="Agregar", width=80, height=34,
                      command=self._buscar_y_agregar).grid(row=0, column=1)

        cols_prod = ("id", "codigo", "nombre", "precio", "stock")
        self.tree_productos = ttk.Treeview(self.panel_productos, columns=cols_prod, show="headings", height=14)

        self.tree_productos.heading("id", text="ID")
        self.tree_productos.heading("codigo", text="Código")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("precio", text="Precio")
        self.tree_productos.heading("stock", text="Stock")

        self.tree_productos.column("id", width=35, anchor="center")
        self.tree_productos.column("codigo", width=100)
        self.tree_productos.column("nombre", width=140)
        self.tree_productos.column("precio", width=70, anchor="center")
        self.tree_productos.column("stock", width=50, anchor="center")

        scroll = ctk.CTkScrollbar(self.panel_productos, command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scroll.set)

        self.tree_productos.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(0, 8))
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 5), pady=(0, 8))

        self.tree_productos.bind("<Double-1>", lambda e: self._agregar_desde_tabla())

        self._cargar_productos()

    def _cargar_productos(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        productos = self.venta_controller.obtener_productos_disponibles()
        for p in productos:
            self.tree_productos.insert("", "end", values=(
                p.id, p.codigo_barras, p.nombre, f"S/ {p.precio:.2f}", p.stock_actual
            ))

    def _crear_panel_carrito(self):
        self.panel_carrito = ctk.CTkFrame(self)
        self.panel_carrito.grid(row=1, column=1, sticky="nsew", padx=(8, 20), pady=(0, 12))
        self.panel_carrito.grid_columnconfigure(0, weight=1)
        self.panel_carrito.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.panel_carrito, text="Carrito",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(10, 6))

        cols = ("nombre", "cant", "precio", "subtotal")
        self.tree_carrito = ttk.Treeview(self.panel_carrito, columns=cols, show="headings", height=8)

        self.tree_carrito.heading("nombre", text="Producto")
        self.tree_carrito.heading("cant", text="Cant.")
        self.tree_carrito.heading("precio", text="Precio")
        self.tree_carrito.heading("subtotal", text="Subtotal")

        self.tree_carrito.column("nombre", width=120)
        self.tree_carrito.column("cant", width=45, anchor="center")
        self.tree_carrito.column("precio", width=65, anchor="center")
        self.tree_carrito.column("subtotal", width=75, anchor="center")

        self.tree_carrito.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 6))

        btn_frame = ctk.CTkFrame(self.panel_carrito, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 6))

        ctk.CTkButton(btn_frame, text="Quitar", width=90, height=30,
                      fg_color="#C0392B", hover_color="#A93226",
                      command=self._quitar).grid(row=0, column=0, padx=(0, 4))

        ctk.CTkButton(btn_frame, text="Limpiar", width=90, height=30,
                      fg_color="gray", hover_color="gray30",
                      command=self._limpiar).grid(row=0, column=1)

        totales_frame = ctk.CTkFrame(self.panel_carrito)
        totales_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 6))
        totales_frame.grid_columnconfigure(0, weight=1)

        row_sub = ctk.CTkFrame(totales_frame, fg_color="transparent")
        row_sub.grid(row=0, column=0, sticky="ew", padx=8, pady=2)
        row_sub.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(row_sub, text="Subtotal:").grid(row=0, column=0, sticky="w")
        self.lbl_subtotal = ctk.CTkLabel(row_sub, text="S/ 0.00")
        self.lbl_subtotal.grid(row=0, column=1, sticky="e")

        row_igv = ctk.CTkFrame(totales_frame, fg_color="transparent")
        row_igv.grid(row=1, column=0, sticky="ew", padx=8, pady=2)
        row_igv.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(row_igv, text="IGV (18%):").grid(row=0, column=0, sticky="w")
        self.lbl_igv = ctk.CTkLabel(row_igv, text="S/ 0.00")
        self.lbl_igv.grid(row=0, column=1, sticky="e")

        row_total = ctk.CTkFrame(totales_frame, fg_color="transparent")
        row_total.grid(row=2, column=0, sticky="ew", padx=8, pady=2)
        row_total.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(row_total, text="TOTAL:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        self.lbl_total = ctk.CTkLabel(row_total, text="S/ 0.00",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_total.grid(row=0, column=1, sticky="e")

        pago_frame = ctk.CTkFrame(self.panel_carrito, fg_color="transparent")
        pago_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(4, 2))

        ctk.CTkLabel(pago_frame, text="Pago:").grid(row=0, column=0, sticky="w")
        self.entry_pago = ctk.CTkEntry(pago_frame, width=80, height=32, placeholder_text="0.00")
        self.entry_pago.grid(row=0, column=1, padx=(6, 8))
        self.entry_pago.bind("<KeyRelease>", lambda e: self._calcular_vuelto())

        ctk.CTkLabel(pago_frame, text="Vuelto:").grid(row=0, column=2, sticky="w")
        self.lbl_vuelto = ctk.CTkLabel(pago_frame, text="S/ 0.00",
                                        font=ctk.CTkFont(weight="bold"))
        self.lbl_vuelto.grid(row=0, column=3, padx=(6, 0))

        self.lbl_msg = ctk.CTkLabel(self.panel_carrito, text="", wraplength=260)
        self.lbl_msg.grid(row=5, column=0, pady=(2, 4))

        ctk.CTkButton(
            self.panel_carrito, text="Realizar Venta", width=200, height=38,
            fg_color="#2FA572", hover_color="#288F62",
            command=self._realizar_venta
        ).grid(row=6, column=0, pady=(0, 10))

    def _buscar_y_agregar(self):
        codigo = self.entry_codigo.get().strip()
        exito, mensaje, producto = self.venta_controller.buscar_producto(codigo)

        if exito:
            ok, msg = self.venta_controller.agregar_al_carrito(producto, 1)
            if ok:
                self._actualizar_carrito()
                self.entry_codigo.delete(0, "end")
                self.entry_codigo.focus()
                self.lbl_msg.configure(text=f"{producto.nombre} agregado", text_color="green")
            else:
                self.lbl_msg.configure(text=msg, text_color="red")
        else:
            self.lbl_msg.configure(text=mensaje, text_color="red")

    def _agregar_desde_tabla(self):
        sel = self.tree_productos.selection()
        if not sel:
            return
        valores = self.tree_productos.item(sel[0])["values"]
        producto_id = valores[0]

        ok, msg = self.venta_controller.agregar_por_id(producto_id, 1)
        if ok:
            self._actualizar_carrito()
            self.lbl_msg.configure(text=f"Producto {valores[2]} agregado", text_color="green")
        else:
            self.lbl_msg.configure(text=msg, text_color="red")

    def _quitar(self):
        sel = self.tree_carrito.selection()
        if not sel:
            return
        index = self.tree_carrito.index(sel[0])
        producto = self.tree_carrito.item(sel[0])["values"]
        self.venta_controller.quitar_del_carrito(index)
        self._actualizar_carrito()
        self.lbl_msg.configure(text=f"Producto {producto[0]} retirado", text_color="red")

    def _limpiar(self):
        self.venta_controller.limpiar_carrito()
        self._actualizar_carrito()
        self.entry_pago.delete(0, "end")
        self.lbl_vuelto.configure(text="S/ 0.00")
        self.lbl_msg.configure(text="Carrito vaciado", text_color="red")

    def _actualizar_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        for item in self.venta_controller.carrito:
            self.tree_carrito.insert("", "end", values=(
                item["nombre"], item["cantidad"],
                f"S/ {item['precio_unitario']:.2f}", f"S/ {item['subtotal']:.2f}"
            ))

        self.lbl_subtotal.configure(text=f"S/ {self.venta_controller.obtener_subtotal():.2f}")
        self.lbl_igv.configure(text=f"S/ {self.venta_controller.obtener_igv():.2f}")
        self.lbl_total.configure(text=f"S/ {self.venta_controller.obtener_total():.2f}")
        self._calcular_vuelto()

    def _calcular_vuelto(self):
        monto = self.entry_pago.get().strip()
        if not monto:
            self.lbl_vuelto.configure(text="S/ 0.00")
            return

        ok, msg, vuelto = self.venta_controller.calcular_vuelto(monto)
        if ok:
            self.lbl_vuelto.configure(text=f"S/ {vuelto:.2f}", text_color="green")
        else:
            self.lbl_vuelto.configure(text=msg, text_color="red")

    def _realizar_venta(self):
        if not self.venta_controller.carrito:
            self.lbl_msg.configure(text="El carrito está vacío", text_color="red")
            return

        monto_str = self.entry_pago.get().strip()
        if not monto_str:
            self.lbl_msg.configure(text="Ingrese el monto pagado", text_color="red")
            return

        ok_pago, msg_pago, vuelto = self.venta_controller.calcular_vuelto(monto_str)
        if not ok_pago:
            self.lbl_msg.configure(text=msg_pago, text_color="red")
            return

        total = self.venta_controller.obtener_total()
        confirmar = messagebox.askyesno(
            "Confirmar Venta",
            f"Total: S/ {total:.2f}\nPagado: S/ {float(monto_str):.2f}\nVuelto: S/ {vuelto:.2f}\n\n¿Confirmar venta?"
        )
        if not confirmar:
            return

        exito, mensaje, datos_pdf = self.venta_controller.realizar_venta()
        if exito:
            monto_pagado = float(monto_str)
            ruta_pdf = self.venta_controller.generar_pdf(datos_pdf, monto_pagado, vuelto)

            self._actualizar_carrito()
            self._cargar_productos()
            self.entry_pago.delete(0, "end")
            self.lbl_vuelto.configure(text="S/ 0.00")
            self.lbl_msg.configure(text=mensaje, text_color="#2FA572")

            abrir = messagebox.askyesno("Venta Exitosa", f"{mensaje}\nVuelto: S/ {vuelto:.2f}\n\n¿Abrir comprobante PDF?")
            if abrir:
                os.startfile(ruta_pdf)
        else:
            self.lbl_msg.configure(text=mensaje, text_color="red")