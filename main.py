import os
import sys
import threading

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog
from datetime import datetime

from utils import check_single_instance
from ProcesamientoAG.processing_AG import main_process_AG
from ProcesamientoAG.detalle_operaciones import main_process_detalle_operacion
from console_redirect import ConsoleRedirect


carpeta = None 

def configurar_apariencia():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

def crear_ventana_principal():
    check_single_instance("ManifiestoCargaPDF")
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("Manifiesto Internacional de Carga | PDF ➜ Excel")
    app.update_idletasks()  # Asegurarse de que las dimensiones estén actualizadas
    ancho_ventana = 800
    alto_ventana = 600
    x_centro = (app.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_centro = (app.winfo_screenheight() // 2) - (alto_ventana // 2)
    app.geometry(f"{ancho_ventana}x{alto_ventana}+{x_centro}+{y_centro}")

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
    archivos = list(archivos)
    carpeta_padre = os.path.dirname(archivos[0]) if archivos else None
    return archivos, carpeta_padre


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
    archivos = getattr(boton, 'archivos_pdf', []) # obt
    if not archivos:
        tk.messagebox.showwarning("Advertencia", "No hay archivos para procesar.")
        return
    
    carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta destino:")
    if not carpeta_destino:
        return
    
    boton.configure(state="disabled", text="⏳ Convirtiendo...", fg_color="#888888")
    boton.update_idletasks()
    def ejecutar():
        try:
            print("------- Iniciando procesamiento -------")
            main_process_AG(archivos, carpeta_destino, carpeta)
            print(f"\nArchivos convertidos a Excel en: {carpeta_destino}\n")
            tk.messagebox.showinfo("Éxito", f"Archivos convertidos a Excel en: {carpeta_destino}")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            tk.messagebox.showerror("Error", f"error: {e}")
        finally:
            boton.configure(state="normal", text="📤 Convertir a Excel", fg_color="#00aa88")
    threading.Thread(target=ejecutar).start()

def crear_detalle_operacion():
    AG_excel = filedialog.askopenfilename(filetypes=[("Seleccionar un AG de empresa especifico", "*.xlsx")], title="Seleccionar archivo Excel (AG de empresa especifico)")
    
    if not AG_excel:
        tk.messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo Excel.")
        return
    
    anio, mes = None, None  # Variables para almacenar el año y el mes seleccionados

    ventana = ctk.CTkToplevel()
    ventana.title("Ingresar Año y Mes")
    ventana.geometry("300x230")
    ventana.grab_set()  # Bloquear interacción con la ventana principal

    # Centrar la ventana en la pantalla
    ventana.update_idletasks()
    ancho_ventana = 300
    alto_ventana = 230
    x_centro = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_centro = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x_centro}+{y_centro}")

    def cerrar_ventana():
        ventana.destroy()

    etiqueta_anio = ctk.CTkLabel(ventana, text="Año:")
    etiqueta_anio.pack(pady=(10, 2))
    anio_actual = datetime.now().year
    anio_input = ctk.CTkComboBox(ventana, values=[str(a) for a in range(anio_actual, anio_actual - 4, -1)])
    anio_input.pack(pady=(0, 5))

    etiqueta_mes = ctk.CTkLabel(ventana, text="Mes:")
    etiqueta_mes.pack(pady=(5, 2))
    mes_actual = datetime.now().month
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_input = ctk.CTkComboBox(ventana, values=meses)
    mes_input.set(meses[mes_actual - 1])  # Seleccionar el mes actual por defecto
    mes_input.pack(pady=(0, 5))

    anio_textinput = ctk.CTkEntry(ventana, placeholder_text="Ingrese el año")
    mes_textinput = ctk.CTkEntry(ventana, placeholder_text="Ingrese el mes")

    def habilitar_textinputs():
        anio_input.pack_forget()
        mes_input.pack_forget()
        etiqueta_mes.pack_forget()
        etiqueta_anio.pack_forget()
        
        anio_textinput.pack(pady=(0, 5))
        mes_textinput.pack(pady=(5, 5))

    boton_escribir_a_mano = ctk.CTkButton(
        ventana, text="🖊️ Escribir a mano", fg_color="#aa3333", hover_color="#cc4444", command=habilitar_textinputs
    )
    boton_escribir_a_mano.pack(pady=(10, 5))

    def confirmar():
        nonlocal anio, mes
        if anio_textinput.winfo_ismapped() and mes_textinput.winfo_ismapped():
            anio = anio_textinput.get()
            mes = mes_textinput.get()
        else:
            anio = anio_input.get()
            mes = mes_input.get()
        if not anio or not mes:
            tk.messagebox.showwarning("Advertencia", "Debe ingresar un año y un mes.")
            return
        cerrar_ventana()

        # Preguntar dónde guardar el archivo Excel resultante
        carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta para guardar el Excel resultante")
        if not carpeta_destino:
            tk.messagebox.showwarning("Advertencia", "Debe seleccionar una carpeta para guardar el archivo.")
            return

        main_process_detalle_operacion('assets/plantilla_detalle_operaciones.xlsx', carpeta_destino, AG_excel, anio, mes)
        

        tk.messagebox.showinfo("Éxito", f"Archivo Excel generado y guardado en: {carpeta_destino}")

    boton_confirmar = ctk.CTkButton(
        ventana, text="Confirmar", fg_color="#00aa88", hover_color="#00ccaa", command=confirmar
    )
    boton_confirmar.pack(pady=(10, 5))

    ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)
    ventana.mainloop()

    
    
    

def accion_seleccionar_carpeta(app, frame, etiqueta, boton_convertir, contador_pdfs):
    global carpeta  # Hacer la variable carpeta global
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
    global carpeta  # Hacer la variable carpeta global
    archivos_absolutos, carpeta = seleccionar_archivos()
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

    boton_detalles = ctk.CTkButton(
        columna_derecha,
        text="📋 Detalle de Operacion",
        fg_color="#00aa88",
        hover_color="#00ccaa",
        width=240,
        height=40,
        command=crear_detalle_operacion,
        font=ctk.CTkFont(size=13, weight="bold")
    )
    mostrar_tooltip(boton_detalles, "Crear un excel -> Detalle de Operacion seleccionando excel especifico (AG-{empresa}, no el AG)")
    boton_detalles.pack(side="bottom", pady=(10, 0))
    
    app.mainloop()
    
if __name__ == "__main__":
    main()