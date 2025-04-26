import time
import os

import pandas as pd
from pdfquery import PDFQuery

from ProcesamientoAG.scrap_pdf_AG import get_datos_from_pdf, check_format, get_TRANSPORTE_CAMPO_9, get_DESTINATARIO
from utils import listar_archivos_pdf
from openpyxl import load_workbook

def trasnform_df_AG(df)->pd.DataFrame:
    """ Transformar el df para que tenga el formato correcto
    y los tipos de datos correctos

    Args:
        df (pd.Dataframe): dataframe a transformar

    Returns:
        pd.DataFrame: dataframe transformado
    """
    

    meses_a_numeros = {
        "ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04",
        "MAY": "05", "JUN": "06", "JUL": "07", "AGO": "08",
        "SEP": "09", "OCT": "10", "NOV": "11", "DIC": "12"
    }

    for mes_texto, mes_numero in meses_a_numeros.items():
        df['FECHA CARGA'] = df['FECHA CARGA'].str.replace(mes_texto, mes_numero, regex=False)

    df['FECHA CARGA'] = pd.to_datetime(df['FECHA CARGA'], format='%d-%m-%y').dt.strftime('%d/%m/%Y')

    df['D.D.T'] = df['D.D.T'].str.extract(r'Destinacion:\s*(.*?)\s*F\. Ofic')
    
    # df['NACIONALIDAD TRANSPORTE']
    
    df['EXPORTADOR'] = df['EXPORTADOR'].str.split('\n').str[0]
    
    #df['PRODUCTO'] = #LOGICA EN BASE AL EXPORTADOR
    
    #SI EL EXPORTADOR ES	LA MERCADERIA ES
    #PBBPOLISUR SOCIEDAD DE RESPONS	POLIETILENO
    #UNIPAR INDUPA SAIC	POLICLORURO DE VINILO
    #COMPA?IA MEGA SOCIEDAD ANONIMA	GAS LICUADO
    #COMPA?IA MOLINERA DEL SUR S. A	SEMOLA DE TRIGO
    #TRANSPORTADORA DE GAS DEL SUR	GAS LICUADO
    #VITERRA ARGENTINA S.A.	ACEITE / PELLETS / LECITINA
    #LA NUEVA MANERA S.A.	HARINA DE TRIGO
    #SYNGENTA	ACEITE
    #SI NO CUMPLE CON LAS ANTERIORES	INDETERMINADO

    df['descripcion_mercancia'] = df['descripcion_mercancia'].str.replace(r'cid:\d+', '', regex=True)

    df

    
    df = df.astype({
        'VALOR FOB': 'float',
        'KILOS BRUTOS': 'float'      
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
            return None
            
            
        data = get_datos_from_pdf(pdf)
        print(f"Procesado {os.path.basename(archivo)} en {time.time() - start:.2f} segundos")
        return data
    except Exception as e:
        print(f"Error {os.path.basename(archivo)}")
        return None

def process_all_pdfs(archivos: list[str]) -> tuple[list, list]:
    """Procesa todos los archivos PDF en la lista de archivos
    y devuelve una lista de diccionarios con los datos obtenidos
    y una lista de archivos válidos.

    Args:
        archivos (list[str]): lista con las rutas

    Returns:
        tuple: (data, archivos_validos)
    """
    start = time.time()
    data = []
    archivos_validos = []

    try:
        for archivo in archivos:
            resultado = process_pdf(archivo)
            if resultado is not None:
                data.append(resultado)
                archivos_validos.append(archivo)
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return [], []
    
    print(f"Procesados {len(archivos_validos)} archivos válidos en {time.time() - start:.2f} segundos")
    return data, archivos_validos

def main_process_AG(archivos: list, destino: str) -> None:
    """
    Procesa todos los archivos PDF, los convierte a df de pandas y los guarda en un archivo Excel.
    Args:
        archivos (list): lista de paths de archivos a procesar
        destino (str): path absoluto
    """
    lista, archivos_validos = process_all_pdfs(archivos)
    
    nombres_archivos = [
        os.path.splitext(os.path.basename(archivo))[0]
        for archivo in archivos_validos
    ]
    
    df = pd.DataFrame(lista)
    
    df.insert(1, 'MIC - DTA', nombres_archivos) 
    
    
    TRANSPORTE_CAMPO_9 = get_TRANSPORTE_CAMPO_9(archivos_validos)
    df['TRANSPORTE CAMPO 9'] = TRANSPORTE_CAMPO_9
    
    DESTINATARIO = get_DESTINATARIO(archivos_validos)
    df['DESTINATARIO'] = DESTINATARIO
    
    #NACIONALIDAD_TRANSPORTE = 
    
    df = trasnform_df_AG(df)
    
    
    df.to_excel(destino, index=False)
    
    workbook = load_workbook(destino)
    sheet = workbook.active

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Obtener la letra de la columna
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        sheet.column_dimensions[column_letter].width = adjusted_width

    workbook.save(destino)
    workbook.close()
    print(f"Acomodando las columnas de excel...")

# dejar un archivo general

# despues dividir por mes y año

if __name__ == "__main__":
    archivos = listar_archivos_pdf('C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/testing-data')
    