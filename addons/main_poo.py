import os
import sys
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from ProcesamientoAG.processing_AG import main_process_AG
from ProcesamientoAG.detalle_operaciones import main_process_detalle_operacion
from utils.utilities import check_single_instance
from utils.console_redirect import ConsoleRedirect

class PDFConverterApp:
    def __init__(self):
        self.carpeta = None
        self.archivos_pdf = []
        self.setup_appearance()
        self.create_main_window()
        self.setup_ui()
        
    def setup_appearance(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def create_main_window(self):
        check_single_instance("ManifiestoCargaPDF")
        self.app = ctk.CTk()
        self.app.geometry("800x600")
        self.app.title("Manifiesto Internacional de Carga | PDF ➜ Excel")
        self.app.update_idletasks()
        
        ancho_ventana = 800
        alto_ventana = 600
        x_centro = (self.app.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y_centro = (self.app.winfo_screenheight() // 2) - (alto_ventana // 2)
        self.app.geometry(f"{ancho_ventana}x{alto_ventana}+{x_centro}+{y_centro}")
        
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "assets", "icon.ico")
        self.app.iconbitmap(icon_path)
    
    def setup_ui(self):
        # Configuración de la interfaz de usuario
        self.create_title()
        self.create_main_container()
        self.create_left_column()
        self.create_right_column()
        
    def create_title(self):
        titulo = ctk.CTkLabel(
            self.app, 
            text="PDF ➜ Excel: Manifiesto Internacional de Carga", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(pady=(20, 10))
    
    def create_main_container(self):
        self.contenedor_principal = ctk.CTkFrame(self.app)
        self.contenedor_principal.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_left_column(self):
        self.columna_izquierda = ctk.CTkFrame(self.contenedor_principal)
        self.columna_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        self.etiqueta_path = ctk.CTkLabel(
            self.columna_izquierda, 
            text="Ninguna carpeta ni archivos seleccionados", 
            anchor="center"
        )
        self.etiqueta_path.pack(pady=(0, 5), fill="x")
        
        self.contador_pdfs = ctk.CTkLabel(self.columna_izquierda, text="", anchor="w")
        self.contador_pdfs.pack(pady=(0, 10), fill="x")
        
        self.frame_scroll = ctk.CTkScrollableFrame(
            self.columna_izquierda, 
            label_text="Archivos PDF encontrados"
        )
        self.frame_scroll.pack(fill="both", expand=True)
        
        self.consola_output = ctk.CTkTextbox(self.columna_izquierda, height=100)
        self.consola_output.pack(fill="x", padx=10, pady=(10, 0))
        sys.stdout = ConsoleRedirect(self.consola_output)
    
    def create_right_column(self):
        self.columna_derecha = ctk.CTkFrame(self.contenedor_principal)
        self.columna_derecha.pack(side="right", fill="y", padx=(10, 0), pady=10)
        
        self.create_folder_button()
        self.create_files_button()
        self.create_convert_button()
        self.create_clear_button()
        self.create_details_button()
    
    def create_folder_button(self):
        self.boton_seleccionar = ctk.CTkButton(
            self.columna_derecha,
            text="📂 Seleccionar carpeta con PDFs",
            command=self.select_folder_action,
            width=240,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"))
        self.show_tooltip(self.boton_seleccionar, "Selecciona una carpeta para procesar todos los PDFs que contiene.")
        self.boton_seleccionar.pack(pady=(0, 10))
    
    def create_files_button(self):
        self.boton_seleccionar_archivos = ctk.CTkButton(
            self.columna_derecha,
            text="📑 Seleccionar archivo(s) PDF",
            command=self.select_files_action,
            width=240,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"))
        self.show_tooltip(self.boton_seleccionar_archivos, "Selecciona archivos PDF específicos para procesar.")
        self.boton_seleccionar_archivos.pack(pady=(0, 20))
    
    def create_convert_button(self):
        self.boton_convertir = ctk.CTkButton(
            self.columna_derecha,
            text="📤 Convertir a Excel",
            fg_color="#434a3a",
            hover_color="#434a3a",
            width=240,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.convert_to_excel,
            state="disabled")
        self.boton_convertir.archivos_pdf = []
        self.show_tooltip(self.boton_convertir, "No se han cargado PDFs todavía")
        self.boton_convertir.pack(pady=(0, 10))
    
    def create_clear_button(self):
        self.boton_limpiar = ctk.CTkButton(
            self.columna_derecha,
            text="🗑️ Limpiar",
            fg_color="#aa3333",
            hover_color="#cc4444",
            width=240,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.clear_state)
        self.show_tooltip(self.boton_limpiar, "Limpiar estado y archivos cargados.")
        self.boton_limpiar.pack()
    
    def create_details_button(self):
        self.boton_detalles = ctk.CTkButton(
            self.columna_derecha,
            text="📋 Detalle de Operacion",
            fg_color="#00aa88",
            hover_color="#00ccaa",
            width=240,
            height=40,
            command=self.create_operation_detail,
            font=ctk.CTkFont(size=13, weight="bold"))
        self.show_tooltip(self.boton_detalles, "Crear un excel -> Detalle de Operacion seleccionando excel especifico")
        self.boton_detalles.pack(side="bottom", pady=(10, 0))
    
    def show_tooltip(self, widget, texto):
        tooltip = ctk.CTkToplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.configure(bg="#333333")
        label = ctk.CTkLabel(tooltip, text=texto, text_color="white", 
                            fg_color="#333333", corner_radius=6, 
                            font=ctk.CTkFont(size=11))
        label.pack(padx=8, pady=4)
        
        def mostrar(event):
            tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            tooltip.deiconify()
        
        def ocultar(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", mostrar, add="+")
        widget.bind("<Leave>", ocultar, add="+")
    
    def select_folder_action(self):
        self.carpeta = filedialog.askdirectory()
        if self.carpeta:
            self.archivos_pdf = [os.path.join(self.carpeta, f) 
                                for f in os.listdir(self.carpeta) 
                                if f.lower().endswith('.pdf')]
            if not self.archivos_pdf:
                self.show_tooltip(self.boton_convertir, "No se han cargado PDFs todavía")
                return
            
            self.show_pdf_files()
            self.update_file_info()
            self.enable_convert_button()
    
    def select_files_action(self):
        archivos = filedialog.askopenfilenames(
            filetypes=[("Archivos PDF", "*.pdf")], 
            title="Seleccionar archivo(s) PDF")
        
        if archivos:
            self.archivos_pdf = list(archivos)
            self.carpeta = os.path.dirname(self.archivos_pdf[0])
            self.show_pdf_files()
            self.update_file_info()
            self.enable_convert_button()
    
    def show_pdf_files(self):
        self.clear_frame(self.frame_scroll)
        for archivo in self.archivos_pdf:
            nombre = os.path.basename(archivo)
            etiqueta = ctk.CTkLabel(self.frame_scroll, text=f'📄 {nombre}', anchor="w")
            etiqueta.pack(anchor="w", padx=10, pady=2)
    
    def update_file_info(self):
        total_peso = sum(os.path.getsize(f) for f in self.archivos_pdf)
        self.contador_pdfs.configure(
            text=f"{len(self.archivos_pdf)} archivo(s) PDF • {round(total_peso / (1024 * 1024), 2)} MB", 
            text_color="gray80")
        
        self.etiqueta_path.configure(
            text=f"📁 {self.carpeta}", 
            anchor="w", 
            cursor="hand2", 
            fg_color="#2e3b4e", 
            corner_radius=8, 
            text_color="white")
        
        self.etiqueta_path.bind("<Button-1>", lambda e: os.startfile(self.carpeta))
        self.etiqueta_path.bind("<Enter>", lambda e: self.etiqueta_path.configure(fg_color="#3f4f68"))
        self.etiqueta_path.bind("<Leave>", lambda e: self.etiqueta_path.configure(fg_color="#2e3b4e"))
    
    def enable_convert_button(self):
        self.boton_convertir.configure(state="normal", fg_color="#00aa88", hover_color="#00ccaa")
        self.boton_convertir.archivos_pdf = self.archivos_pdf
        self.boton_convertir.unbind("<Enter>")
        self.boton_convertir.unbind("<Leave>")
    
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
        frame.update_idletasks()
        try:
            frame._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass
    
    def convert_to_excel(self):
        if not self.archivos_pdf:
            tk.messagebox.showwarning("Advertencia", "No hay archivos para procesar.")
            return
        
        carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta destino:")
        if not carpeta_destino:
            return
        
        self.boton_convertir.configure(state="disabled", text="⏳ Convirtiendo...", fg_color="#888888")
        self.boton_convertir.update_idletasks()
        
        def ejecutar():
            try:
                print("------- Iniciando procesamiento -------")
                main_process_AG(self.archivos_pdf, carpeta_destino, self.carpeta)
                print(f"\nArchivos convertidos a Excel en: {carpeta_destino}\n")
                tk.messagebox.showinfo("Éxito", f"Archivos convertidos a Excel en: {carpeta_destino}")
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                tk.messagebox.showerror("Error", f"error: {e}")
            finally:
                self.boton_convertir.configure(
                    state="normal", 
                    text="📤 Convertir a Excel", 
                    fg_color="#00aa88")
        
        threading.Thread(target=ejecutar).start()
    
    def clear_state(self):
        self.etiqueta_path.configure(
            text="Ninguna carpeta seleccionada", 
            anchor="center", 
            fg_color="transparent", 
            text_color="white", 
            cursor="arrow")
        self.etiqueta_path.pack_configure(padx=0)
        self.etiqueta_path.unbind("<Enter>")
        self.etiqueta_path.unbind("<Leave>")
        self.etiqueta_path.unbind("<Button-1>")
        
        self.clear_frame(self.frame_scroll)
        self.contador_pdfs.configure(text="")
        
        self.boton_convertir.configure(
            state="disabled", 
            fg_color="#434a3a", 
            hover_color="#434a3a")
        self.boton_convertir.unbind("<Enter>")
        self.boton_convertir.unbind("<Leave>")
        self.boton_convertir.archivos_pdf = []
        
        self.show_tooltip(self.boton_convertir, "No se han cargado PDFs todavía")
        self.archivos_pdf = []
        self.carpeta = None
    
    def create_operation_detail(self):
        AG_excel = filedialog.askopenfilename(
            filetypes=[("Seleccionar un AG de empresa especifico", "*.xlsx")], 
            title="Seleccionar archivo Excel (AG de empresa especifico)")
        
        if not AG_excel:
            tk.messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo Excel.")
            return
        
        ventana = ctk.CTkToplevel()
        ventana.title("Ingresar Año y Mes")
        ventana.geometry("300x230")
        ventana.grab_set()
        
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
        mes_input.set(meses[mes_actual - 1])
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
            ventana, 
            text="🖊️ Escribir a mano", 
            fg_color="#aa3333", 
            hover_color="#cc4444", 
            command=habilitar_textinputs)
        boton_escribir_a_mano.pack(pady=(10, 5))
        
        def confirmar():
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
            carpeta_destino = filedialog.askdirectory(
                title="Seleccionar carpeta para guardar el Excel resultante")
            
            if not carpeta_destino:
                tk.messagebox.showwarning("Advertencia", "Debe seleccionar una carpeta para guardar el archivo.")
                return
            
            main_process_detalle_operacion(
                'assets/plantilla_detalle_operaciones.xlsx', 
                carpeta_destino, 
                AG_excel, 
                anio, 
                mes)
            
            tk.messagebox.showinfo("Éxito", f"Archivo Excel generado y guardado en: {carpeta_destino}")
        
        boton_confirmar = ctk.CTkButton(
            ventana, 
            text="Confirmar", 
            fg_color="#00aa88", 
            hover_color="#00ccaa", 
            command=confirmar)
        boton_confirmar.pack(pady=(10, 5))
        
        ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)
        ventana.mainloop()
    
    def iniciar(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = PDFConverterApp()
    app.iniciar()