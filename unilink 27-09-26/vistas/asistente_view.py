import customtkinter as ctk


class AsistenteView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, fg_color="#0B1120", corner_radius=20, **kwargs)
        self.controller = controller
        self.collapsed = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_propagate(False)

        self.message_index = 0
        self._crear_componentes()

    def _crear_componentes(self):
        self.header = ctk.CTkFrame(self, fg_color="#111827", corner_radius=20)
        self.header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.header.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(
            self.header,
            text="Asistente UNILINK",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#E5E7EB",
            anchor="w"
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=12, pady=12)

        self.subtitle = ctk.CTkLabel(
            self.header,
            text="Comandos locales para inventario, ventas y navegación.",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            anchor="w"
        )
        self.subtitle.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))

        self.toggle_btn = ctk.CTkButton(
            self.header,
            text="◀",
            width=36,
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=18,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._toggle_collapsed
        )
        self.toggle_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=12)

        self.collapsed_frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=20)
        self.collapsed_frame.grid(row=0, column=0, sticky="ns", padx=12, pady=(12, 8))
        self.collapsed_frame.grid_columnconfigure(0, weight=1)
        self.collapsed_frame.grid_rowconfigure(0, weight=1)
        self.collapsed_frame.grid_remove()

        self.min_toggle_btn = ctk.CTkButton(
            self.collapsed_frame,
            text="▶",
            width=36,
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=18,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._toggle_collapsed
        )
        self.min_toggle_btn.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#111827",
            border_width=1,
            border_color="#334155",
            corner_radius=20,
            label_text=""
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self._crear_panel_entrada()

    def _toggle_collapsed(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.chat_frame.grid_remove()
            self.panel_entrada.grid_remove()
            self.header.grid_remove()
            self.collapsed_frame.grid()
            self.configure(width=70)
        else:
            self.collapsed_frame.grid_remove()
            self.header.grid()
            self.chat_frame.grid()
            self.panel_entrada.grid()
            self.configure(width=300)

    def _crear_panel_entrada(self):
        self.panel_entrada = ctk.CTkFrame(self, fg_color="#111827", corner_radius=20)
        self.panel_entrada.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.panel_entrada.grid_columnconfigure(0, weight=1)

        sugerencias = [
            "¿Stock bajo?",
            "¿Ventas de hoy?",
            "Ir a Productos",
            "Buscar producto"
        ]
        sugerencia_frame = ctk.CTkFrame(self.panel_entrada, fg_color="transparent")
        sugerencia_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 10))
        for idx, texto in enumerate(sugerencias):
            btn = ctk.CTkButton(
                sugerencia_frame,
                text=texto,
                height=28,
                fg_color="#1F2937",
                hover_color="#334155",
                text_color="#E5E7EB",
                corner_radius=14,
                font=ctk.CTkFont(size=11),
                command=lambda t=texto: self._on_quick_command(t)
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 8, 0))
            sugerencia_frame.grid_columnconfigure(idx, weight=1)

        bottom_frame = ctk.CTkFrame(self.panel_entrada, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.entry_comando = ctk.CTkEntry(
            bottom_frame,
            placeholder_text="Escribe un comando...",
            fg_color="#0F172A",
            text_color="#E5E7EB",
            border_color="#334155",
            width=92,
            height=36,
            corner_radius=14
        )
        self.entry_comando.grid(row=0, column=0, sticky="ew", pady=(0, 0), padx=(0, 10))
        self.entry_comando.bind("<Return>", lambda event: self._enviar_mensaje())

        enviar_btn = ctk.CTkButton(
            bottom_frame,
            text=">",
            width=48,
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=16,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._enviar_mensaje
        )
        enviar_btn.grid(row=0, column=1)

    def _on_quick_command(self, texto):
        self.entry_comando.delete(0, "end")
        self.entry_comando.insert(0, texto)
        self._enviar_mensaje()

    def _enviar_mensaje(self):
        texto = self.entry_comando.get().strip()
        if not texto:
            return

        self.agregar_mensaje_usuario(texto)
        self.entry_comando.delete(0, "end")

        if self.controller:
            self.controller.procesar_mensaje(texto)

    def agregar_mensaje_usuario(self, texto):
        self._agregar_burbuja(texto, sender="user")

    def agregar_mensaje_asistente(self, texto):
        self._agregar_burbuja(texto, sender="assistant")

    def _agregar_burbuja(self, texto, sender="assistant"):
        contenedor = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        contenedor.grid(row=self.message_index, column=0, sticky="ew", padx=12, pady=6)
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)

        color_burbuja = "#1D4ED8" if sender == "user" else "#0F766E"
        texto_color = "#F8FAFC" if sender == "user" else "#ECFCCB"
        alineacion_col = 1 if sender == "user" else 0
        padding = (0, 60) if sender == "user" else (60, 0)

        burbuja = ctk.CTkFrame(contenedor, fg_color=color_burbuja, corner_radius=18)
        burbuja.grid(row=0, column=alineacion_col, sticky="w" if sender == "assistant" else "e", padx=padding)

        etiqueta = ctk.CTkLabel(
            burbuja,
            text=texto,
            wraplength=340,
            justify="left",
            text_color=texto_color,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        etiqueta.grid(row=0, column=0, padx=14, pady=12, sticky="w")

        self.message_index += 1
        self.chat_frame.update_idletasks()
        try:
            self.chat_frame._canvas.yview_moveto(1.0)
        except Exception:
            pass
