import time
import os

import pandas as pd
from pdfquery import PDFQuery

from scrap_pdf import get_datos_from_pdf
from utils import listar_archivos_pdf


def process_pdf(archivo:str)->dict:
    start = time.time()
    """ Procesa un archivo PDF y obtiene los datos que se buscan
    Args:
        archivo (str): ruta del archivo PDF a procesar

    Returns:
        data: diccionario con los datos obtenidos del PDF
    """
    try:
        pdf = PDFQuery(archivo)
        pdf.load(0)
        data = get_datos_from_pdf(pdf)
        print(f"Procesado {archivo} en {time.time() - start:.2f} segundos")
        return data
    except Exception as e:
        print(f"Error procesando {archivo}: {e}")
        return None

def process_all_pdfs(archivos: list[str])->list:
    """ Procesa todos los archivos PDF en la lista de archivos
    y devuelve una lista de diccionarios con los datos obtenidos

    Args:
        archivos (list[str]): lista con las rutas

    Returns:
        list: data que despues se convertira a un dataframe
    """
    start = time.time()
    
    try:
        data = list(map(process_pdf, archivos))
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None
    print(f"Procesados {len(archivos)} archivos en {time.time() - start:.2f} segundos")
    return data

def main_process(archivos: list,destino: str)->None:
    """
    Procesa todos los archivos PDF, los convierte a df de pandas y los guarda en un archivo Excel
    Args:
        archivos (list): lista de paths de archivos a procesar
        destino (str): path absoluto
    """
   
    lista = process_all_pdfs(archivos)
    df = pd.DataFrame(lista)
    df.to_excel(destino, index=False)


# dejar un archivo general

# despues dividir por mes y año

if __name__ == "__main__":
    archivos = listar_archivos_pdf('C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/testing-data/03-MARZO-2025/')
    
    lista = process_all_pdfs(archivos)
    df = pd.DataFrame(lista)
    print(df)
    df.to_excel('data/data.xlsx', index=False)