
import sys
import ctypes
import os

def check_single_instance(app_name):
    """
    Para que no se pueda abrir más de una instancia de la aplicación.
    """
    try:
        # Intenta crear un mutex con un nombre único
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, app_name)
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.user32.MessageBoxW(0, "La aplicación ya está en ejecución.", "Error", 0x10)
            sys.exit(1)
    except Exception as e:
        print(f"Error al verificar instancia: {e}")
        sys.exit(1)

def listar_archivos(directorio):
    archivos = []
    for file in os.listdir(directorio):
        if os.path.isfile(os.path.join(directorio, file)):
            archivos.append(file)
    return archivos

def pdf_a_xml(pdf) -> None:
    pdf.tree.write('output.xml', encoding='utf-8', xml_declaration=True, pretty_print=True)