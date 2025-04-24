import time
import os

import pandas as pd
from pdfquery import PDFQuery

from scrap_pdf import get_datos_from_pdf, check_format
from utils import listar_archivos_pdf

def trasnform_df(df)->pd.DataFrame:
    """ Transformar el df para que tenga el formato correcto
    y los tipos de datos correctos

    Args:
        df (pd.Dataframe): dataframe a transformar

    Returns:
        pd.DataFrame: dataframe transformado
    """
    
    df['documentos_anexos'] = df['documentos_anexos'].str.extract(r'Destinacion:\s*(.*?)\s*F\. Ofic')
    
    df['conductor'] = df['conductor'].str.extract(r'CONDUCTOR\s*\d*:\s*(.*)')
    
    
    df = df.astype({
        'valor_FOT': 'float',
        'flete_usd': 'float',
        'cantidad_bultos': 'int',
        'peso_bruto': 'float'      
    })
    
    return df


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
        
        if not check_format(pdf):
            print(f"Formato incorrecto para {archivo}")
            return None
            
        data = get_datos_from_pdf(pdf)
        print(f"Procesado {os.path.basename(archivo)} en {time.time() - start:.2f} segundos")
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
        data = [resultado for resultado in map(process_pdf, archivos) if resultado is not None]
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None
    print(f"Procesados {len(archivos)} archivos en {time.time() - start:.2f} segundos")
    return data

def main_process(archivos: list, destino: str) -> None:
    """
    Procesa todos los archivos PDF, los convierte a df de pandas y los guarda en un archivo Excel
    Args:
        archivos (list): lista de paths de archivos a procesar
        destino (str): path absoluto
    """
    lista = process_all_pdfs(archivos)
    
    nombres_archivos = [
        os.path.splitext(os.path.basename(archivo))[0]
        for archivo, resultado in zip(archivos, lista) if resultado is not None
    ]
    
    df = pd.DataFrame(lista)
    
    df.insert(0, 'archivo', nombres_archivos) 
    df = trasnform_df(df)
    
    # Guardar el df en el archivo Excel
    df.to_excel(destino, index=False)


# dejar un archivo general

# despues dividir por mes y año

if __name__ == "__main__":
    archivos = listar_archivos_pdf('C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/testing-data/03-MARZO-2025/')
    
    lista = process_all_pdfs(archivos)
    df = pd.DataFrame(lista)
    print(df)
    df.to_excel('data/data.xlsx', index=False)