
import sys
import ctypes
import os

from functools import partial

from pdfquery import PDFQuery

def check_single_instance(app_name):
    """
    Para que no se pueda abrir más de una instancia de la aplicación.
    """
    try:
        # Intenta crear un mutex con un nombre único
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, app_name)
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.user32.MessageBoxW(0, "La aplicación ya esta en ejecucion.", "Error", 0x10)
            sys.exit(1)
    except Exception as e:
        print(f"Error al verificar instancia: {e}")
        sys.exit(1)

def listar_archivos(directorio, formato=None):
    """
    Lista los archivos en un directorio dado con un formato especifico.
    Si no se especifica un formato, lista todos los archivos.
    Retorna las rutas absolutas.
    """
    directorio = os.path.abspath(directorio)  # asegura que el path sea absoluto
    archivos = []
    for file in os.listdir(directorio):
        path_completo = os.path.join(directorio, file)
        if os.path.isfile(path_completo) and (formato is None or file.lower().endswith(formato.lower())):
            archivos.append(path_completo)
    return archivos

listar_archivos_pdf = partial(listar_archivos, formato='.pdf') 
__all__ = ['listar_archivos_pdf'] 
# la agrega al namespace del modulo, ya que es una funcion parcial, y no se puede importar directamente

def convertir_pdf_a_xml(pdf_path, output_path=None):
    """
    Convierte un archivo PDF a XML utilizando pdfquery.

    Args:
        pdf_path (str): Ruta del archivo PDF.
        output_path (str, optional): Ruta donde se guardará el archivo XML. 
                                     Si no se proporciona, se guardará junto al PDF con extensión .xml.

    Returns:
        str: Ruta del archivo XML generado.
    """

    # Cargar el archivo PDF
    pdf = PDFQuery(pdf_path)
    pdf.load(0)  

    if output_path is None:
        output_path = pdf_path.replace('.pdf', '.xml')

    
    pdf.tree.write(output_path, pretty_print=True, encoding="utf-8")
    return output_path
    
if __name__ == "__main__":
    print(listar_archivos_pdf('C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/testing-data'))