import customtkinter as ctk


class VentaView(ctk.CTkFrame):
    """Vista de terminal de venta y facturación."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F4F6F8", corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_layout()

    def _build_layout(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(main, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Terminal de venta", text_color="#111827", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        search = ctk.CTkEntry(left, placeholder_text="Buscar producto, código o categoría", height=38)
        search.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        catalog = ctk.CTkFrame(left, fg_color="#F8FAFC")
        catalog.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        catalog.grid_columnconfigure((0, 1, 2), weight=1)

        for i in range(6):
            item = ctk.CTkFrame(catalog, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
            item.grid(row=i // 3, column=i % 3, sticky="nsew", padx=8, pady=8)
            ctk.CTkLabel(item, text=f"Producto {i + 1}", text_color="#111827", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(12, 4))
            ctk.CTkLabel(item, text="S/ 18.90", text_color="#2FA572", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(0, 12))
            ctk.CTkButton(item, text="Agregar", width=120, fg_color="#2FA572", hover_color="#237D58", corner_radius=10).pack(pady=(0, 12))

        right = ctk.CTkFrame(main, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7ECEF")
        right.grid(row=0, column=1, sticky="nsew", pady=(0, 12))
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Factura / ticket", text_color="#111827", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        details = ctk.CTkTextbox(right, height=220, fg_color="#F8FAFC", border_color="#E2E8F0", border_width=1)
        details.grid(row=1, column=0, sticky="ew", padx=18)
        details.insert("end", "1. Producto A\tS/ 18.90\n2. Producto B\tS/ 24.50\n")
        details.configure(state="disabled")

        totals = ctk.CTkFrame(right, fg_color="transparent")
        totals.grid(row=2, column=0, sticky="ew", padx=18, pady=(16, 10))
        totals.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(totals, text="Subtotal", text_color="#64748B").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(totals, text="S/ 43.40", text_color="#111827", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(totals, text="IVA", text_color="#64748B").grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(totals, text="S/ 7.81", text_color="#111827", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=1, sticky="e")
        ctk.CTkLabel(totals, text="Total", text_color="#111827", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, sticky="w", pady=(8, 0))
        ctk.CTkLabel(totals, text="S/ 51.21", text_color="#2FA572", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=1, sticky="e", pady=(8, 0))

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(actions, text="Cobrar", fg_color="#2FA572", hover_color="#237D58", height=42).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(actions, text="Cancelar", fg_color="#E2E8F0", text_color="#0F172A", hover_color="#CBD5E1", height=42).grid(row=0, column=1, sticky="ew", padx=(8, 0))
