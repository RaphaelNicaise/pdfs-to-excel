import os
import sys
import threading

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog

from utils import check_single_instance
from ProcesamientoAG.processing_AG import main_process_AG
from console_redirect import ConsoleRedirect


def configurar_apariencia():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

def crear_ventana_principal():
    check_single_instance("ManifiestoCargaPDF")
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("Manifiesto Internacional de Carga | PDF ➜ Excel")
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    icon_path = os.path.join(base_path, "assets", "icon.ico")
    app.iconbitmap(icon_path)
    return app

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

def seleccionar_carpeta():
    return filedialog.askdirectory()

def seleccionar_archivos():
    archivos = filedialog.askopenfilenames(filetypes=[("Archivos PDF", "*.pdf")], title="Seleccionar archivo(s) PDF")
    return list(archivos)

def mostrar_archivos_pdf(frame, archivos_absolutos):
    limpiar_frame(frame)
    for archivo in archivos_absolutos:
        nombre = os.path.basename(archivo)
        etiqueta = ctk.CTkLabel(frame, text=f'📄 {nombre}', anchor="w")
        etiqueta.pack(anchor="w", padx=10, pady=2)

def limpiar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.update_idletasks()
    try:
        frame._parent_canvas.yview_moveto(0.0)
    except Exception:
        pass

def convertir_a_excel():
    boton = convertir_a_excel.boton
    archivos = getattr(boton, 'archivos_pdf', [])
    if not archivos:
        tk.messagebox.showwarning("Advertencia", "No hay archivos para procesar.")
        return
    nombre_archivo = simpledialog.askstring("Nombre del archivo", "Ingrese el nombre para el archivo Excel (sin extensión):")
    if not nombre_archivo:
        return
    carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta destino para Excel")
    if not carpeta_destino:
        return
    excel_path = os.path.join(carpeta_destino, f"{nombre_archivo}.xlsx")
    boton.configure(state="disabled", text="⏳ Convirtiendo...", fg_color="#888888")
    boton.update_idletasks()
    def ejecutar():
        try:
            print("------- Iniciando procesamiento -------")
            main_process_AG(archivos, excel_path)
            print(f"\nArchivos convertidos a Excel en: {excel_path}\n")
            tk.messagebox.showinfo("Éxito", f"Archivos convertidos a Excel en: {excel_path}")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            tk.messagebox.showerror("Error", f"error: {e}")
        finally:
            boton.configure(state="normal", text="📤 Convertir a Excel", fg_color="#00aa88")
    threading.Thread(target=ejecutar).start()

def accion_seleccionar_carpeta(app, frame, etiqueta, boton_convertir, contador_pdfs):
    carpeta = seleccionar_carpeta()
    if carpeta:
        archivos_absolutos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.lower().endswith('.pdf')]
        if not archivos_absolutos:
            mostrar_tooltip(boton_convertir, "No se han cargado PDFs todavía")
            return
        mostrar_archivos_pdf(frame, archivos_absolutos)
        total_peso = sum(os.path.getsize(f) for f in archivos_absolutos)
        contador_pdfs.configure(text=f"{len(archivos_absolutos)} archivo(s) PDF • {round(total_peso / (1024 * 1024), 2)} MB", text_color="gray80")
        etiqueta.configure(text=f"📁 {carpeta}", anchor="w", cursor="hand2", fg_color="#2e3b4e", corner_radius=8, text_color="white")
        etiqueta.bind("<Button-1>", lambda e: os.startfile(carpeta))
        etiqueta.bind("<Enter>", lambda e: etiqueta.configure(fg_color="#3f4f68"))
        etiqueta.bind("<Leave>", lambda e: etiqueta.configure(fg_color="#2e3b4e"))
        boton_convertir.configure(state="normal", fg_color="#00aa88", hover_color="#00ccaa")
        boton_convertir.archivos_pdf = archivos_absolutos

        # Eliminar el tooltip del botón convertir
        boton_convertir.unbind("<Enter>")
        boton_convertir.unbind("<Leave>")

def accion_seleccionar_archivos(app, frame, etiqueta, boton_convertir, contador_pdfs):
    archivos_absolutos = seleccionar_archivos()
    if archivos_absolutos:
        mostrar_archivos_pdf(frame, archivos_absolutos)
        total_peso = sum(os.path.getsize(f) for f in archivos_absolutos)
        carpeta = os.path.dirname(archivos_absolutos[0])
        contador_pdfs.configure(text=f"{len(archivos_absolutos)} archivo(s) PDF • {round(total_peso / (1024 * 1024), 2)} MB", text_color="gray80")
        etiqueta.configure(text=f"📁 {carpeta}", anchor="w", cursor="hand2", fg_color="#2e3b4e", corner_radius=8, text_color="white")
        etiqueta.bind("<Button-1>", lambda e: os.startfile(carpeta))
        etiqueta.bind("<Enter>", lambda e: etiqueta.configure(fg_color="#3f4f68"))
        etiqueta.bind("<Leave>", lambda e: etiqueta.configure(fg_color="#2e3b4e"))
        boton_convertir.configure(state="normal", fg_color="#00aa88", hover_color="#00ccaa")
        boton_convertir.archivos_pdf = archivos_absolutos

        # Eliminar el tooltip del botón convertir
        boton_convertir.unbind("<Enter>")
        boton_convertir.unbind("<Leave>")



def limpiar_estado(frame, etiqueta, boton_convertir, contador_pdfs):
    """
    Limpia el estado de la interfaz, eliminando archivos cargados y deshabilitando el botón de conversión.
    """
    etiqueta.configure(text="Ninguna carpeta seleccionada", anchor="center", fg_color="transparent", text_color="white", cursor="arrow")
    etiqueta.pack_configure(padx=0)
    etiqueta.unbind("<Enter>")
    etiqueta.unbind("<Leave>")
    etiqueta.unbind("<Button-1>")
    limpiar_frame(frame)
    contador_pdfs.configure(text="")
    boton_convertir.configure(state="disabled", fg_color="#434a3a", hover_color="#434a3a")
    boton_convertir.unbind("<Enter>")
    boton_convertir.unbind("<Leave>")
    boton_convertir.archivos_pdf = []

    
    mostrar_tooltip(boton_convertir, "No se han cargado PDFs todavía")

def main():
    
    
    

    configurar_apariencia()
    app = crear_ventana_principal()

    titulo = ctk.CTkLabel(app, text="PDF ➜ Excel: Manifiesto Internacional de Carga", font=ctk.CTkFont(size=20, weight="bold"))
    titulo.pack(pady=(20, 10))

    contenedor_principal = ctk.CTkFrame(app)
    contenedor_principal.pack(fill="both", expand=True, padx=20, pady=10)

    columna_izquierda = ctk.CTkFrame(contenedor_principal)
    columna_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

    etiqueta_path = ctk.CTkLabel(columna_izquierda, text="Ninguna carpeta ni archivos seleccionados", anchor="center")
    etiqueta_path.pack(pady=(0, 5), fill="x")

    contador_pdfs = ctk.CTkLabel(columna_izquierda, text="", anchor="w")
    contador_pdfs.pack(pady=(0, 10), fill="x")

    frame_scroll = ctk.CTkScrollableFrame(columna_izquierda, label_text="Archivos PDF encontrados")
    frame_scroll.pack(fill="both", expand=True)

    consola_output = ctk.CTkTextbox(columna_izquierda, height=100)
    consola_output.pack(fill="x", padx=10, pady=(10, 0))
    sys.stdout = ConsoleRedirect(consola_output)
    
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
    mostrar_tooltip(boton_seleccionar, "Selecciona una carpeta para procesar todos los PDFs que contiene.")
    boton_seleccionar.pack(pady=(0, 10))

    boton_seleccionar_archivos = ctk.CTkButton(
        columna_derecha,
        text="📑 Seleccionar archivo(s) PDF",
        command=lambda: accion_seleccionar_archivos(app, frame_scroll, etiqueta_path, boton_convertir, contador_pdfs),
        width=240,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    mostrar_tooltip(boton_seleccionar_archivos, "Selecciona archivos PDF específicos para procesar.")
    boton_seleccionar_archivos.pack(pady=(0, 20))

    global boton_convertir
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
    convertir_a_excel.boton = boton_convertir
    boton_convertir.archivos_pdf = []
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
    mostrar_tooltip(boton_limpiar, "Limpiar estado y archivos cargados.")
    boton_limpiar.pack()


    app.mainloop()
if __name__ == "__main__":
    main()