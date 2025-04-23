import os
import sys

import customtkinter as ctk
from tkinter import filedialog

from utils import check_single_instance

# ------------------- CONFIGURACIÓN DE LA APP -------------------

def configurar_apariencia():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

def crear_ventana_principal():
    
    check_single_instance("ManifiestoCargaPDF")
    
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("Manifiesto Internacional de Carga | PDF ➜ Excel")
    
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.dirname(__file__)
        
    icon_path = os.path.join(base_path, "assets", "icon.ico")
    app.iconbitmap(icon_path)
    
    return app

# ------------------- TOOLTIP -------------------

def mostrar_tooltip(widget, texto):
    tooltip = ctk.CTkToplevel()
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip.configure(bg="#333333")
    label = ctk.CTkLabel(tooltip, text=texto, text_color="white", fg_color="#333333", corner_radius=6, font=ctk.CTkFont(size=11))
    label.pack(padx=8, pady=4)

    def mostrar(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def ocultar(event):
        tooltip.withdraw()

    widget.bind("<Enter>", mostrar, add="+")
    widget.bind("<Leave>", ocultar, add="+")

# ------------------- FUNCIONES PRINCIPALES -------------------

def seleccionar_carpeta():
    return filedialog.askdirectory()

def mostrar_archivos_pdf(frame, carpeta):
    limpiar_frame(frame)
    archivos_pdf = [f for f in os.listdir(carpeta) if f.lower().endswith('.pdf')]
    for archivo in archivos_pdf:
        etiqueta = ctk.CTkLabel(frame, text=f'📄 {archivo}', anchor="w")
        etiqueta.pack(anchor="w", padx=10, pady=2)
    return archivos_pdf

def limpiar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def convertir_a_excel():
    """
    Logica
    """
    ...
    

# ------------------- FUNCIONES DE INTERFAZ -------------------

def accion_seleccionar_carpeta(app, frame, etiqueta, boton_convertir, contador_pdfs):
    carpeta = seleccionar_carpeta()
    if carpeta:
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        etiqueta.configure(
            text=f"📁 {carpeta}",
            anchor="w",
            cursor="hand2",
            fg_color="#2e3b4e",
            corner_radius=8,
            text_color="white"
        )
        etiqueta.pack_configure(padx=0)  # para evitar centrado
        etiqueta.bind("<Button-1>", lambda e: os.startfile(carpeta))
        etiqueta.bind("<Enter>", lambda e: etiqueta.configure(fg_color="#3f4f68"))
        etiqueta.bind("<Leave>", lambda e: etiqueta.configure(fg_color="#2e3b4e"))

        archivos_pdf = mostrar_archivos_pdf(frame, carpeta)
        total_peso = sum(os.path.getsize(os.path.join(carpeta, f)) for f in archivos_pdf)
        contador_pdfs.configure(
            text=f"{len(archivos_pdf)} archivo(s) PDF • {round(total_peso / (1024 * 1024), 2)} MB",
            text_color="gray80"
        )

        if archivos_pdf:
            boton_convertir.configure(state="normal", fg_color="#00aa88", hover_color="#00ccaa")
            boton_convertir.unbind("<Enter>")
            boton_convertir.unbind("<Leave>")
        else:
            boton_convertir.configure(state="disabled", fg_color="#434a3a", hover_color="#434a3a")
            mostrar_tooltip(boton_convertir, "No se han cargado PDFs todavía")
    else:
        limpiar_estado(frame, etiqueta, boton_convertir, contador_pdfs)

def limpiar_estado(frame, etiqueta, boton_convertir, contador_pdfs):
    etiqueta.configure(
        text="Ninguna carpeta seleccionada",
        anchor="center",
        fg_color="transparent",
        text_color="white",
        cursor="arrow"
    )
    etiqueta.pack_configure(padx=0)
    etiqueta.unbind("<Enter>")
    etiqueta.unbind("<Leave>")
    etiqueta.unbind("<Button-1>")

    limpiar_frame(frame)
    contador_pdfs.configure(text="")
    boton_convertir.configure(state="disabled", fg_color="#434a3a", hover_color="#434a3a")
    boton_convertir.unbind("<Enter>")
    boton_convertir.unbind("<Leave>")
    print("Path limpiado")

# ------------------- EJECUCIÓN -------------------

def main():
    configurar_apariencia()
    app = crear_ventana_principal()

    titulo = ctk.CTkLabel(app, text="PDF ➜ Excel: Manifiesto Internacional de Carga", font=ctk.CTkFont(size=20, weight="bold"))
    titulo.pack(pady=(20, 10))

    contenedor_principal = ctk.CTkFrame(app)
    contenedor_principal.pack(fill="both", expand=True, padx=20, pady=10)

    # -------- COLUMNA IZQUIERDA --------
    columna_izquierda = ctk.CTkFrame(contenedor_principal)
    columna_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

    etiqueta_path = ctk.CTkLabel(columna_izquierda, text="Ninguna carpeta seleccionada", anchor="center")
    etiqueta_path.pack(pady=(0, 5), fill="x")

    contador_pdfs = ctk.CTkLabel(columna_izquierda, text="", anchor="w")
    contador_pdfs.pack(pady=(0, 10), fill="x")

    frame_scroll = ctk.CTkScrollableFrame(columna_izquierda, label_text="Archivos PDF encontrados")
    frame_scroll.pack(fill="both", expand=True)

    # -------- COLUMNA DERECHA --------
    columna_derecha = ctk.CTkFrame(contenedor_principal)
    columna_derecha.pack(side="right", fill="y", padx=(10, 0), pady=10)

    boton_seleccionar = ctk.CTkButton(
        columna_derecha,
        text="📂 Seleccionar carpeta con PDFs",
        command=lambda: accion_seleccionar_carpeta(app, frame_scroll, etiqueta_path, boton_convertir, contador_pdfs),
        width=240,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    boton_seleccionar.pack(pady=(0, 20))

    boton_convertir = ctk.CTkButton(
        columna_derecha,
        text="📤 Convertir a Excel",
        fg_color="#434a3a",
        hover_color="#434a3a",
        width=240,
        height=40,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=convertir_a_excel,
        state="disabled"
    )
    boton_convertir.pack(pady=(0, 10))
    mostrar_tooltip(boton_convertir, "No se han cargado PDFs todavía")

    boton_limpiar = ctk.CTkButton(
        columna_derecha,
        text="🗑️ Limpiar",
        fg_color="#aa3333",
        hover_color="#cc4444",
        width=240,
        height=40,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: limpiar_estado(frame_scroll, etiqueta_path, boton_convertir, contador_pdfs)
    )
    boton_limpiar.pack()

    app.mainloop()

if __name__ == "__main__":
    main()
