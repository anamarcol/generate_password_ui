import customtkinter as ctk
from tkinter import filedialog
import generator
import excel_manager
import string
import os
import subprocess

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


BG_APP    = "#F2F2F7" 
BG_CARD   = "#FFFFFF"
BG_INPUT  = "#F2F2F7"
BORDER    = "#D1D1D6"
PINK      = "#FF2D78"
PINK_SOFT = "#FF6FA3"
PINK_PALE = "#FFE5EE"
TEXT_MAIN = "#1C1C1E"
TEXT_DIM  = "#6E6E73"
TEXT_MUTED= "#AEAEB2"
GREEN_IOS = "#34C759"
GOLD      = "#FF9F0A"

def _font(size=14, weight="normal"):
    for fam in ("SF Pro Display", "SF Pro Text", "-apple-system", "Helvetica Neue", "DejaVu Sans"):
        try:
            return ctk.CTkFont(family=fam, size=size, weight=weight)
        except Exception:
            continue
    return ctk.CTkFont(size=size, weight=weight)


class PillButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        self._base_color = kw.get("fg_color", PINK)
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda _: self.configure(fg_color=PINK_SOFT))
        self.bind("<Leave>", lambda _: self.configure(fg_color=self._base_color))


class IOSCard(ctk.CTkFrame):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", BG_CARD)
        kw.setdefault("corner_radius", 13)
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", BORDER)
        super().__init__(master, **kw)


class IOSEntry(ctk.CTkEntry):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", BG_INPUT)
        kw.setdefault("border_width", 0)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("text_color", TEXT_MAIN)
        kw.setdefault("height", 36)
        super().__init__(master, **kw)


class IOSProgress(ctk.CTkProgressBar):
    """Barra de progreso estilo iOS — delgada, rosa, sin borde."""

    def __init__(self, master, width=460, **kw):
        super().__init__(
            master,
            width=width,
            height=6,
            corner_radius=3,
            fg_color="#E5E5EA",
            progress_color=PINK,
            border_width=0,
            **kw,
        )
        self.set(0)


class FloatingHeart(ctk.CTkLabel):
    """Corazoncito que flota hacia arriba y desaparece."""

    SYMBOLS = ["♡", "♡", "♡", "✿", "♡"]
    COLORS  = [PINK, PINK_SOFT, "#FF6B9D", "#FF4D8D", PINK_SOFT]

    def __init__(self, master, x, y):
        import random
        idx = random.randint(0, len(self.SYMBOLS) - 1)
        size = random.randint(13, 20)
        super().__init__(
            master,
            text=self.SYMBOLS[idx],
            font=_font(size),
            text_color=self.COLORS[idx],
            fg_color="transparent",
        )
        self._x  = x + random.randint(-18, 18)
        self._y  = y
        self._dy = random.uniform(1.8, 3.2)
        self._dx = random.uniform(-0.6, 0.6)
        self._life = 0
        self._max  = random.randint(42, 58)
        self.place(x=self._x, y=self._y)
        self._step()

    def _step(self):
        self._life += 1
        if self._life >= self._max:
            self.destroy()
            return
        self._y -= self._dy
        self._x += self._dx
        self.place(x=int(self._x), y=int(self._y))
        self.after(28, self._step)


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SecurePass Generator")
        self.geometry("1000x700")
        self.configure(fg_color=BG_APP)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.df = None

        # ── HEADER ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_CARD, height=64,
                              corner_radius=0, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        row = ctk.CTkFrame(header, fg_color="transparent")
        row.grid(row=0, column=0, pady=16)

        ctk.CTkLabel(row, text="🔐", font=_font(22),
                     fg_color="transparent", text_color=PINK).pack(side="left", padx=(0,8))

        ctk.CTkLabel(row, text="SecurePass Generator",
                     font=_font(22, "bold"),
                     text_color=TEXT_MAIN, fg_color="transparent").pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=BORDER,
                     corner_radius=0).grid(row=0, column=0, sticky="sew")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        container.grid_columnconfigure((0,1,2), weight=1, uniform="col")

        archivo_panel = IOSCard(container)
        archivo_panel.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(archivo_panel, text="ARCHIVO EXCEL",
                     font=_font(10, "bold"), text_color=TEXT_MUTED,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(14,0))

        self.boton_cargar = PillButton(
            archivo_panel,
            text="Cargar Excel",
            height=38, width=160, corner_radius=19,
            font=_font(13, "bold"),
            fg_color=PINK, hover_color=PINK_SOFT, text_color="white",
            border_width=0,
            command=self.cargar_excel
        )
        self.boton_cargar.pack(pady=(10,8), padx=16, anchor="w")

        badge = ctk.CTkFrame(archivo_panel, fg_color=PINK_PALE,
                             corner_radius=10, border_width=0)
        badge.pack(fill="x", padx=16, pady=(0,14))

        ctk.CTkLabel(badge, text="Correos cargados",
                     font=_font(10), text_color=PINK,
                     fg_color="transparent").pack(pady=(8,0))

        self.label_correos = ctk.CTkLabel(
            badge, text="0",
            font=_font(28, "bold"), text_color=PINK,
            fg_color="transparent")
        self.label_correos.pack(pady=(0,8))

        letras_panel = IOSCard(container)
        letras_panel.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(letras_panel, text="CONFIGURACIÓN LETRAS",
                     font=_font(10, "bold"), text_color=TEXT_MUTED,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(14,0))

        ctk.CTkLabel(letras_panel, text="Cantidad",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(8,2))

        self.letras = IOSEntry(letras_panel, width=80)
        self.letras.insert(0, "3")
        self.letras.pack(anchor="w", padx=16)

        ctk.CTkFrame(letras_panel, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(letras_panel, text="Tipo de caracteres",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(0,6))

        self.mayusculas = ctk.CTkCheckBox(
            letras_panel, text="Usar MAYÚSCULAS",
            font=_font(13), text_color=TEXT_MAIN,
            fg_color=PINK, hover_color=PINK_SOFT,
            checkmark_color="white", border_color=BORDER, corner_radius=6)
        self.mayusculas.select()
        self.mayusculas.pack(anchor="w", padx=16, pady=4)

        self.minusculas = ctk.CTkCheckBox(
            letras_panel, text="Usar minúsculas",
            font=_font(13), text_color=TEXT_MAIN,
            fg_color=PINK, hover_color=PINK_SOFT,
            checkmark_color="white", border_color=BORDER, corner_radius=6)
        self.minusculas.pack(anchor="w", padx=16, pady=(0,14))

        numeros_panel = IOSCard(container)
        numeros_panel.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(numeros_panel, text="DÍGITOS PERMITIDOS",
                     font=_font(10, "bold"), text_color=TEXT_MUTED,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(14,0))

        ctk.CTkLabel(numeros_panel, text="Cantidad",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(8,2))

        self.digitos = IOSEntry(numeros_panel, width=80)
        self.digitos.insert(0, "3")
        self.digitos.pack(anchor="w", padx=16)

        ctk.CTkFrame(numeros_panel, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(numeros_panel, text="Caracteres disponibles",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", padx=16, pady=(0,2))

        self.digitos_entry = IOSEntry(numeros_panel, width=160)
        self.digitos_entry.insert(0, "0123456789")
        self.digitos_entry.pack(anchor="w", padx=16, pady=(0,14))

        simbolos_panel = IOSCard(container)
        simbolos_panel.grid(row=1, column=0, columnspan=3, padx=8, pady=8, sticky="ew")

        inner = ctk.CTkFrame(simbolos_panel, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        inner.grid_columnconfigure((0,1), weight=1)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(left, text="SÍMBOLOS PERMITIDOS",
                     font=_font(10, "bold"), text_color=TEXT_MUTED,
                     fg_color="transparent").pack(anchor="w")

        ctk.CTkLabel(left, text="Cantidad",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", pady=(8,2))

        self.simbolos = IOSEntry(left, width=80)
        self.simbolos.insert(0, "2")
        self.simbolos.pack(anchor="w")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.grid(row=0, column=1, sticky="ew", padx=(20,0))
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Caracteres disponibles",
                     font=_font(12), text_color=TEXT_DIM,
                     fg_color="transparent").pack(anchor="w", pady=(0,2))

        self.simbolos_entry = IOSEntry(right)
        self.simbolos_entry.insert(0, "!@#$%")
        self.simbolos_entry.pack(fill="x")

        self.boton_generar = PillButton(
            self,
            text="Generar contraseñas",
            height=45, width=240, corner_radius=22,
            font=_font(15, "bold"),
            fg_color=PINK, hover_color=PINK_SOFT, text_color="white",
            border_width=0,
            command=self.generar
        )
        self.boton_generar.grid(row=2, column=0, pady=(12,6))

        self.progress = IOSProgress(self, width=460)
        self.progress.grid(row=3, column=0, pady=8)

        self.label_combinaciones = ctk.CTkLabel(
            self,
            text="Espacio de claves:",
            font=_font(13),
            text_color=TEXT_DIM,
            fg_color="transparent"
        )
        self.label_combinaciones.grid(row=4, column=0, pady=4)

        self.export = PillButton(
            self,
            text="Exportar Excel",
            height=38, width=180, corner_radius=19,
            font=_font(13, "bold"),
            fg_color=BG_CARD, hover_color=PINK_PALE,
            text_color=PINK,
            border_width=1, border_color=PINK,
            command=self.exportar
        )
        self.export.grid(row=5, column=0, pady=(4,20))

    def _spawn_hearts(self, x, y, n=8):
        for _ in range(n):
            FloatingHeart(self, x, y)

    # ── Actions ───────────────────────────────────────────────────────────
    def cargar_excel(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if ruta:
            self.df = excel_manager.cargar_excel(ruta)
            self.label_correos.configure(text=str(len(self.df)))
            self.boton_cargar.configure(text="✓  Excel cargado", fg_color=GREEN_IOS)
            self.boton_cargar._base_color = GREEN_IOS
            bx = self.boton_cargar.winfo_x() + self.boton_cargar.winfo_width() // 2
            by = self.boton_cargar.winfo_y()
            self._spawn_hearts(bx, by, n=10)

    def generar(self):
        if self.df is None:
            self.label_combinaciones.configure(
                text="⚠  Primero carga un archivo Excel", text_color=GOLD)
            return

        letras_n   = int(self.letras.get())
        digitos_n  = int(self.digitos.get())
        simbolos_n = int(self.simbolos.get())

        letras_set = ""
        if self.mayusculas.get():
            letras_set += string.ascii_uppercase
        if self.minusculas.get():
            letras_set += string.ascii_lowercase

        digitos_set  = list(self.digitos_entry.get())
        simbolos_set = list(self.simbolos_entry.get())

        passwords = []
        total = len(self.df)

        self.label_combinaciones.configure(
            text="Generando contraseñas...", text_color=TEXT_DIM)

        passwords = []
        password_hashes = []

        for i in range(total):
            password, password_hash = generator.generar_password(
                letras_n, digitos_n, simbolos_n,
                letras_set, digitos_set, simbolos_set
            )

            passwords.append(password)
            password_hashes.append(password_hash)

            self.progress.set((i+1)/total)
            self.update()

        self.df["password"] = passwords
        self.df["password_hash"] = password_hashes

        combinaciones = generator.calcular_combinaciones(
            letras_n, digitos_n, simbolos_n,
            letras_set, digitos_set, simbolos_set)

        self.label_combinaciones.configure(
            text=f"Espacio de claves posible: {combinaciones:,}",
            text_color=PINK)
        bx = self.boton_generar.winfo_x() + self.boton_generar.winfo_width() // 2
        by = self.boton_generar.winfo_y()
        self._spawn_hearts(bx, by, n=14)

    def exportar(self):
        if self.df is None:
            self.label_combinaciones.configure(
                text="⚠  No hay datos para exportar", text_color=GOLD)
            return

        os.makedirs("output", exist_ok=True)
        ruta = os.path.join("output", "credenciales_generadas.xlsx")
        excel_manager.guardar_excel(self.df, ruta)
        self.label_combinaciones.configure(
            text=f"Guardado en: {ruta}", text_color=GREEN_IOS)
        bx = self.export.winfo_x() + self.export.winfo_width() // 2
        by = self.export.winfo_y()
        self._spawn_hearts(bx, by, n=10)
        subprocess.Popen(["explorer.exe", "credenciales_generadas.xlsx"], cwd="output")


if __name__ == "__main__":
    app = App()
    app.mainloop()