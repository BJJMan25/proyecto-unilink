import customtkinter as ctk
from tkinter import messagebox

from services.currency_service import CurrencyService


class CurrencyStatusWidget(ctk.CTkFrame):
    """Badge reutilizable en el encabezado/principal para mostrar la tasa del día."""

    def __init__(self, parent, currency_service: CurrencyService | None = None, **kwargs):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#E7ECEF", **kwargs)
        self.currency_service = currency_service or CurrencyService()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.status_dot = ctk.CTkLabel(self, text="●", font=ctk.CTkFont(size=14, weight="bold"), text_color="#16A34A")
        self.status_dot.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="w")

        self.rate_label = ctk.CTkLabel(
            self,
            text="Tasa del día: 1 USD = 0.00 BS",
            text_color="#111827",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.rate_label.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)

        self.refresh_button = ctk.CTkButton(
            self,
            text="🔄",
            width=38,
            height=28,
            corner_radius=8,
            fg_color="#EAF8F2",
            hover_color="#D9F1E6",
            text_color="#0F172A",
            command=self.force_refresh,
        )
        self.refresh_button.grid(row=0, column=2, padx=(0, 12), pady=8, sticky="e")

        self.refresh_status()

    def refresh_status(self):
        estado, tasa, texto = self.currency_service.obtener_estado_tasa()
        if tasa is not None:
            self.rate_label.configure(text=f"Tasa del día: {texto}")
        else:
            self.rate_label.configure(text="Tasa del día: sin información disponible")

        if estado == "actualizada_hoy":
            self.status_dot.configure(text_color="#16A34A")
        else:
            self.status_dot.configure(text_color="#F59E0B")

    def force_refresh(self):
        self.refresh_button.configure(state="disabled")
        try:
            tasa, ok, mensaje = self.currency_service.sincronizar_tasa(force=True)
            if ok and tasa is not None:
                self.rate_label.configure(text=f"Tasa del día: 1 USD = {float(tasa):.2f} BS")
                self.status_dot.configure(text_color="#16A34A")
            else:
                self.rate_label.configure(text=f"Tasa del día: {mensaje}")
                self.status_dot.configure(text_color="#F59E0B")
        finally:
            self.after(800, lambda: self.refresh_button.configure(state="normal"))


class CurrencyUpdateDialog(ctk.CTkToplevel):
    """Modal para administración manual de la tasa de cambio."""

    def __init__(self, parent, currency_service: CurrencyService):
        super().__init__(parent)
        self.currency_service = currency_service
        self.title("Ajuste manual de tasa de cambio")
        self.geometry("420x240")
        self.minsize(360, 220)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color="#F4F6F8")

        main = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18)
        main.pack(fill="both", expand=True, padx=18, pady=18)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main,
            text="Actualizar tasa manualmente",
            text_color="#111827",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        ctk.CTkLabel(
            main,
            text="Valor de 1 USD en BS",
            text_color="#475569",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        self.entry = ctk.CTkEntry(main, placeholder_text="Ej: 36.85", height=38)
        self.entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        current = self.currency_service.obtener_tasa_actual()
        if current is not None:
            self.entry.insert(0, f"{float(current):.4f}")

        footer = ctk.CTkFrame(main, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="e", padx=18, pady=(0, 18))

        ctk.CTkButton(
            footer,
            text="Cancelar",
            width=110,
            height=36,
            fg_color="#64748B",
            hover_color="#475569",
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            footer,
            text="Guardar",
            width=140,
            height=36,
            fg_color="#2FA572",
            hover_color="#248963",
            command=self._guardar,
        ).grid(row=0, column=1)

    def _guardar(self):
        try:
            valor = float(self.entry.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido.")
            return

        ok, mensaje, _ = self.currency_service.actualizar_manual(valor)
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("640x220")

    service = CurrencyService()
    widget = CurrencyStatusWidget(root, currency_service=service)
    widget.pack(fill="x", padx=20, pady=18)
    root.mainloop()
