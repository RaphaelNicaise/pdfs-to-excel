import os
import sys
import threading

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog

from utils import check_single_instance
from processing import main_process
from console_redirect import ConsoleRedirect

# ------------------- Configuración de apariencia -------------------
def configurar_apariencia():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

# ------------------- Ventana principal -------------------
def crear_ventana_principal():
    check_single_instance("ManifiestoCargaPDF")
    app = ctk.CTk()
    app.geometry("900x650")
    app.title("Procesamiento de Archivos PDF")

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)

    icon_path = os.path.join(base_path, "assets", "icon.ico")
    app.iconbitmap(icon_path)
    return app

# ------------------- Tooltip -------------------
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

# ------------------- Funciones de archivo -------------------
def seleccionar_carpeta():
    return filedialog.askdirectory()

def seleccionar_archivos():
    return list(filedialog.askopenfilenames(filetypes=[("Archivos PDF", "*.pdf")], title="Seleccionar archivo(s) PDF"))

def mostrar_archivos_pdf(frame, archivos_absolutos):
    for widget in frame.winfo_children():
        widget.destroy()
    for archivo in archivos_absolutos:
        nombre = os.path.basename(archivo)
        etiqueta = ctk.CTkLabel(frame, text=f'📄 {nombre}', anchor="w")
        etiqueta.pack(anchor="w", padx=10, pady=2)

def procesar_archivos(tipo):
    def convertir():
        boton = convertir.boton
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
                if tipo == "AG":
                    main_process(archivos, excel_path)
                else:
                    main_process(archivos, excel_path)
                print(f"\nArchivos convertidos a Excel en: {excel_path}\n")
                tk.messagebox.showinfo("Éxito", f"Archivos convertidos a Excel en: {excel_path}")
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                tk.messagebox.showerror("Error", f"Error: {e}")
            finally:
                boton.configure(state="normal", text="📤 Convertir a Excel", fg_color="#00aa88")

        threading.Thread(target=ejecutar).start()

    return convertir

def construir_interfaz(app, tipo, frame_parent):
    titulo_texto = "Manifiesto Internacional de Carga" if tipo == "AG" else "DECLARACION JURADA DE VENTA AL EXTERIOR"
    ctk.CTkLabel(frame_parent, text=titulo_texto, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 5))

    etiqueta_path = ctk.CTkLabel(frame_parent, text="Ninguna carpeta ni archivos seleccionados", anchor="center")
    etiqueta_path.pack(pady=(0, 5), fill="x")

    contador_pdfs = ctk.CTkLabel(frame_parent, text="", anchor="w")
    contador_pdfs.pack(pady=(0, 10), fill="x")

    frame_scroll = ctk.CTkScrollableFrame(frame_parent, label_text="Archivos PDF encontrados")
    frame_scroll.pack(fill="both", expand=True)

    consola_output = ctk.CTkTextbox(frame_parent, height=100)
    consola_output.pack(fill="x", padx=10, pady=(10, 0))
    sys.stdout = ConsoleRedirect(consola_output)

    frame_botones = ctk.CTkFrame(frame_parent)
    frame_botones.pack(pady=10)

    def actualizar_estado(archivos):
        mostrar_archivos_pdf(frame_scroll, archivos)
        total_peso = sum(os.path.getsize(f) for f in archivos)
        carpeta = os.path.dirname(archivos[0])
        contador_pdfs.configure(text=f"{len(archivos)} archivo(s) PDF • {round(total_peso / (1024 * 1024), 2)} MB")
        etiqueta_path.configure(text=f"📁 {carpeta}", anchor="w", cursor="hand2", fg_color="#2e3b4e", text_color="white")
        etiqueta_path.bind("<Button-1>", lambda e: os.startfile(carpeta))
        convertir_boton.configure(state="normal", fg_color="#00aa88", hover_color="#00ccaa")
        convertir_boton.archivos_pdf = archivos

    seleccionar_carpeta_btn = ctk.CTkButton(
        frame_botones, text="📂 Seleccionar carpeta con PDFs", width=240, height=40,
        command=lambda: actualizar_estado([os.path.join(seleccionar_carpeta(), f) for f in os.listdir(seleccionar_carpeta()) if f.lower().endswith('.pdf')]),
        font=ctk.CTkFont(size=14, weight="bold")
    )
    seleccionar_carpeta_btn.pack(pady=(0, 10))

    seleccionar_archivos_btn = ctk.CTkButton(
        frame_botones, text="📑 Seleccionar archivo(s) PDF", width=240, height=40,
        command=lambda: actualizar_estado(seleccionar_archivos()),
        font=ctk.CTkFont(size=14, weight="bold")
    )
    seleccionar_archivos_btn.pack(pady=(0, 20))

    global convertir_boton
    convertir_boton = ctk.CTkButton(
        frame_botones, text="📤 Convertir a Excel", width=240, height=40, state="disabled",
        fg_color="#434a3a", hover_color="#434a3a", font=ctk.CTkFont(size=13, weight="bold"),
        command=procesar_archivos(tipo)
    )
    convertir_boton.archivos_pdf = []
    convertir_boton.pack(pady=(0, 10))
    mostrar_tooltip(convertir_boton, "No se han cargado PDFs todavía")

    limpiar_btn = ctk.CTkButton(
        frame_botones, text="🗑️ Limpiar", fg_color="#aa3333", hover_color="#cc4444",
        width=240, height=40, font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: mostrar_archivos_pdf(frame_scroll, [])
    )
    limpiar_btn.pack()

# ------------------- Main -------------------
def main():
    configurar_apariencia()
    app = crear_ventana_principal()

    pestañas = ctk.CTkTabview(app, width=850, height=600)
    pestañas.pack(padx=20, pady=20)

    tab_ag = pestañas.add("AG")
    tab_djve = pestañas.add("Report DJVE")

    construir_interfaz(app, "AG", tab_ag)
    construir_interfaz(app, "DJVE", tab_djve)

    app.mainloop()

if __name__ == "__main__":
    main()
