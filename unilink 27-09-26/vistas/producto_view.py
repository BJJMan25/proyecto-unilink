import customtkinter as ctk
from tkinter import ttk, messagebox
from modelo.producto import Producto

class ProductoView(ctk.CTkFrame):
    def __init__(self, parent, producto_controller, solo_listado=False):
        super().__init__(parent, fg_color="transparent")

        self.producto_controller = producto_controller
        self.solo_listado = solo_listado
        self.btn_frame = None
        self.bind("<Configure>", self._ajustar_layout)
        self._crear_header()
        self._crear_tabla()
        self._crear_botones_accion()
        self._cargar_productos()
        self.after(50, self._ajustar_layout)

    def _ajustar_layout(self, event=None):
        if self.btn_frame is None:
            return

        ancho = max(self.winfo_width(), 1)
        for child in self.btn_frame.winfo_children():
            child.grid_forget()

        if ancho < 900:
            botones = self.btn_frame.winfo_children()
            for idx, btn in enumerate(botones):
                fila = idx // 2
                col = idx % 2
                btn.grid(row=fila, column=col, padx=(0, 6), pady=4, sticky="ew")
            self.btn_frame.grid_columnconfigure((0, 1), weight=1)
        else:
            botones = self.btn_frame.winfo_children()
            for idx, btn in enumerate(botones):
                btn.grid(row=0, column=idx, padx=(0, 6), pady=0, sticky="ew")
            self.btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def _crear_header(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Gestión de Inventario",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        if self.solo_listado:
            ctk.CTkButton(
                header, text="Registrar Entrada", width=150, height=34,
                command=self._abrir_formulario_stock
            ).grid(row=0, column=1, sticky="e")
        else:
            ctk.CTkButton(
                header, text="+ Nuevo Producto", width=150, height=34,
                command=self._abrir_formulario_nuevo
            ).grid(row=0, column=1, sticky="e")

    def _crear_tabla(self):
        # CORRECCIÓN: Forzamos la búsqueda mediante importación relativa segura para evitar caídas
        try:
            from ..assets.styles.estilos import estilizar_tabla
            estilizar_tabla()
        except (ModuleNotFoundError, ImportError):
            try:
                from ..recursos.styles.estilos import estilizar_tabla
                estilizar_tabla()
            except (ModuleNotFoundError, ImportError):
                print("[ADVERTENCIA] No se encontró el módulo de estilos en la raíz. Renderizando Treeview estándar.")

        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 12))
        tabla_frame.grid_columnconfigure(0, weight=1)
        tabla_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "codigo_barras", "nombre", "precio", "stock_actual")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=12)

        self.tree.heading("id", text="ID")
        self.tree.heading("codigo_barras", text="Código Barras")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("stock_actual", text="Stock")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("codigo_barras", width=120)
        self.tree.column("nombre", width=200)
        self.tree.column("precio", width=100, anchor="center")
        self.tree.column("stock_actual", width=100, anchor="center")

        scroll = ctk.CTkScrollbar(tabla_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=8)

    def _crear_botones_accion(self):
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 18))

        if not self.solo_listado:
            ctk.CTkButton(
                self.btn_frame, text="Editar", width=120, height=34,
                fg_color="#2FA572", hover_color="#288F62",
                command=self._editar_producto
            )

            ctk.CTkButton(
                self.btn_frame, text="Eliminar", width=120, height=34,
                fg_color="#C0392B", hover_color="#A93226",
                command=self._eliminar_producto
            )

            ctk.CTkButton(
                self.btn_frame, text="Refrescar", width=120, height=34,
                fg_color="gray", hover_color="gray30",
                command=self._cargar_productos
            )
        else:
            ctk.CTkButton(
                self.btn_frame, text="Registrar Entrada", width=150, height=34,
                command=self._abrir_formulario_stock
            )

            ctk.CTkButton(
                self.btn_frame, text="Refrescar", width=120, height=34,
                fg_color="gray", hover_color="gray30",
                command=self._cargar_productos
            )

        self._ajustar_layout()

    def _cargar_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = self.producto_controller.obtener_productos() or []
        for p in productos:
            self.tree.insert("", "end", values=(
                p.id, p.codigo_barras, p.nombre, p.precio, p.stock_actual
            ))

    def _obtener_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un producto")
            return None
        return self.tree.item(sel[0])["values"]

    def _eliminar_producto(self):
        valores = self._obtener_seleccion()
        if not valores:
            return

        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{valores[2]}'?")
        if not confirmar:
            return

        exito, mensaje = self.producto_controller.eliminar_producto(valores[0])
        if exito:
            self._cargar_productos()
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    def _editar_producto(self):
        valores = self._obtener_seleccion()
        if not valores:
            return

        producto_id = valores[0]
        producto = self.producto_controller.obtener_producto_por_id(producto_id)
        
        if not producto:
            messagebox.showerror("Error", "No se pudo obtener la información del producto")
            return

        datos = {
            "id": producto.id,
            "codigo_barras": producto.codigo_barras,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock_actual": producto.stock_actual
        }
        self._abrir_formulario_editar(datos)

    def _abrir_formulario_nuevo(self):
        self._abrir_formulario(modo="nuevo")

    def _abrir_formulario_editar(self, datos):
        self._abrir_formulario(modo="editar", datos=datos)

    def _abrir_formulario_stock(self):
        valores = self._obtener_seleccion()
        if not valores:
            return

        producto_id = valores[0]
        producto = self.producto_controller.obtener_producto_por_id(producto_id)
        if not producto:
            messagebox.showerror("Error", "No se encontró el producto seleccionado")
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registrar Entrada de Stock")
        dialogo.geometry("420x300")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dialogo, text=f"Producto: {producto.nombre}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(25, 10), padx=20)
        ctk.CTkLabel(dialogo, text=f"Stock actual: {producto.stock_actual}").grid(row=1, column=0, pady=(0, 10), padx=20)

        entry_cantidad = ctk.CTkEntry(dialogo, placeholder_text="Cantidad a agregar", width=300, height=36)
        entry_cantidad.grid(row=2, column=0, pady=(0, 16))

        def guardar_entrada():
            cantidad = entry_cantidad.get().strip()
            if not cantidad:
                messagebox.showerror("Error", "Ingrese una cantidad")
                return

            exito, mensaje = self.producto_controller.agregar_stock(producto.id, cantidad)
            if exito:
                self._cargar_productos()
                messagebox.showinfo("Éxito", mensaje)
                dialogo.destroy()
            else:
                messagebox.showerror("Error", mensaje)

        ctk.CTkButton(dialogo, text="Guardar Entrada", width=300, height=38, command=guardar_entrada).grid(row=3, column=0, pady=(0, 15))

    def _abrir_formulario(self, modo="nuevo", datos=None):
        if modo == "nuevo":
            titulo = "Nuevo Producto"
        else:
            titulo = "Editar Producto"

        dialogo = ctk.CTkToplevel(self)
        dialogo.title(titulo)
        dialogo.geometry("400x500")
        dialogo.resizable(False, False)

        try:
            from config import ICON_PATH
            dialogo.after(200, lambda: dialogo.iconbitmap(ICON_PATH))
        except ImportError:
            pass
        
        dialogo.grab_set()
        dialogo.transient(self.winfo_toplevel())
        dialogo.grid_columnconfigure(0, weight=1)

        row_idx = 0
        ctk.CTkLabel(
            dialogo, text=titulo,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row_idx, column=0, pady=(25, 18))
        row_idx += 1

        entry_codigo_barras = ctk.CTkEntry(dialogo, placeholder_text="Código de barras", width=300, height=36)
        entry_codigo_barras.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_nombre = ctk.CTkEntry(dialogo, placeholder_text="Nombre", width=300, height=36)
        entry_nombre.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_precio = ctk.CTkEntry(dialogo, placeholder_text="Precio", width=300, height=36)
        entry_precio.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        entry_stock_actual = ctk.CTkEntry(dialogo, placeholder_text="Stock actual", width=300, height=36)
        entry_stock_actual.grid(row=row_idx, column=0, pady=(0, 10))
        row_idx += 1

        if datos:
            entry_codigo_barras.insert(0, str(datos["codigo_barras"]))
            entry_nombre.insert(0, str(datos["nombre"]))
            entry_precio.insert(0, str(datos["precio"]))
            entry_stock_actual.insert(0, str(datos["stock_actual"]))

        def guardar():
            # CORRECCIÓN: Validación visual rápida para evitar cruces de tipos de datos vacíos
            if not entry_nombre.get().strip() or not entry_precio.get().strip():
                messagebox.showerror("Error", "Nombre y precio son campos obligatorios.")
                return

            if modo == "nuevo":
                producto = Producto(
                    codigo_barras=entry_codigo_barras.get().strip(),
                    nombre=entry_nombre.get().strip(),
                    precio=entry_precio.get().strip(),
                    stock_actual=entry_stock_actual.get().strip()
                )
                exito, mensaje = self.producto_controller.registrar_producto(producto)
            else:
                producto = Producto(
                    id=datos["id"],
                    codigo_barras=entry_codigo_barras.get().strip(),
                    nombre=entry_nombre.get().strip(),
                    precio=entry_precio.get().strip(),
                    stock_actual=entry_stock_actual.get().strip()
                )
                exito, mensaje = self.producto_controller.actualizar_producto(producto)

            if exito:
                self._cargar_productos()
                messagebox.showinfo("Éxito", mensaje)
                dialogo.destroy()
            else:
                messagebox.showerror("Error", mensaje) 

        if modo == "editar":
            btn_texto = "Actualizar"
        else:
            btn_texto = "Registrar"
            
        ctk.CTkButton(dialogo, text=btn_texto, width=300, height=38, command=guardar).grid(row=row_idx, column=0, pady=(15, 15))