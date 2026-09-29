class NLPEngine:
    INTENCIONES = {
        "ir_a": ["ir a", "abrir", "pantalla", "modulo", "módulo", "productos"],
        "buscar_producto": ["busca", "buscar", "inventario", "hay", "producto"],
        "stock_bajo": ["stock bajo", "bajo stock", "poco stock", "agotado", "stock?"],
        "ver_ventas": ["ventas", "vendi", "ganancia", "facturación", "ingresos"],
        "saludo": ["hola", "buenos", "buenas", "saludo"],
        "despedida": ["gracias", "hasta luego", "adiós", "chau", "bye"]
    }

    def __init__(self):
        pass

    def analizar(self, texto):
        texto_limpio = texto.lower().strip()
        if not texto_limpio:
            return {"intencion": "ninguna", "argumento": ""}

        for intencion, claves in self.INTENCIONES.items():
            if any(clave in texto_limpio for clave in claves):
                argumento = self._extraer_argumento(intencion, texto_limpio)
                return {"intencion": intencion, "argumento": argumento}

        palabras = texto_limpio.split()
        argumento = palabras[-1] if len(palabras) > 1 else ""
        return {"intencion": "desconocida", "argumento": argumento}

    def _extraer_argumento(self, intencion, texto_limpio):
        palabras = texto_limpio.split()

        if intencion == "ir_a":
            for palabra in ["a", "al", "a la", "abrir", "ir", "mostrar"]:
                if palabra in texto_limpio:
                    posible = texto_limpio.split(palabra, 1)[-1].strip()
                    if posible:
                        return posible
            return ""

        if intencion == "buscar_producto":
            for prefijo in ["buscar", "busca", "tengo", "hay", "producto", "stock"]:
                if texto_limpio.startswith(prefijo):
                    posible = texto_limpio.replace(prefijo, "", 1).strip()
                    if posible:
                        return posible
            return ""

        if intencion == "ver_ventas":
            return texto_limpio

        return texto_limpio
