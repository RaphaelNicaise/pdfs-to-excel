import time
import os
import re

import pandas as pd
from pdfquery import PDFQuery

from folders import (
    integrate_files
)
from ProcesamientoAG.scrap_pdf_AG import (
    get_datos_from_pdf, 
    check_format, 
    get_TRANSPORTE_CAMPO_9, 
    get_DESTINATARIO,
    get_NACIONALIDAD_TRANSPORTE
)

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
    
    print("Transformando el conjunto de datos...")
    
    meses_a_numeros = {
        "ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04",
        "MAY": "05", "JUN": "06", "JUL": "07", "AGO": "08",
        "SEP": "09", "OCT": "10", "NOV": "11", "DIC": "12"
    }

    for mes_texto, mes_numero in meses_a_numeros.items():
        df['FECHA CARGA'] = df['FECHA CARGA'].str.replace(mes_texto, mes_numero, regex=False)

    df['FECHA CARGA'] = pd.to_datetime(df['FECHA CARGA'], format='%d-%m-%y').dt.strftime('%d/%m/%Y')

    df['D.D.T'] = df['D.D.T'].str.extract(r'Destinacion:\s*(.*?)\s*F\. Ofic')
    
    
    df['EXPORTADOR'] = df['EXPORTADOR'].str.split('\n').str[0]
    
    df = transform_campo9(df)

    df['PRODUCTO'] = map_producto(df['EXPORTADOR'])

    df['descripcion_mercancia'] = df['descripcion_mercancia'].str.replace(r'cid:\d+', '', regex=True)
    
    df = agregar_factura_y_orden(df)
    
    df = df.astype({
        'VALOR FOB': 'float',
        'KILOS BRUTOS': 'float'      
    })
    
    # ORDENAR COLUMNAS
    orden = [
        'FECHA CARGA',
        'MIC - DTA',
        'C.R.T.',
        'D.D.T',
        'ORDEN',
        'FACTURA Nº',
        'EXPORTADOR',
        'DESTINATARIO',
        'TRANSPORTE CAMPO 1',
        'NACIONALIDAD TRANSPORTE',
        'TRANSPORTE CAMPO 9',
        'TRACTOR',
        'SEMI',
        'DESTINO',
        'ADUANA DESTINO',
        'PRODUCTO',
        'KILOS BRUTOS',
        'VALOR FOB',
        'PRECINTO'
    ]
    
    df = df[orden]
    
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
    
    print(f"Procesados {len(archivos_validos)} archivos válidos en {(time.time() - start):.2f} segundos")
    return data, archivos_validos

def main_process_AG(archivos: list, destino: str, path_carpeta_archivos) -> None:
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
    
     
    df['NACIONALIDAD TRANSPORTE'] = get_NACIONALIDAD_TRANSPORTE(archivos_validos)
    
    df = trasnform_df_AG(df)
    # REORDENAR COLUMNAS
    integrate_files(destino, df, path_carpeta_archivos)
    

# funcion para mapear el exportador al producto, se crea aca porque es una transformacion en base a otro campo, y no un scrapeo
def map_producto(exportador: pd.Series) -> pd.Series:
        """Mapea el exportador al producto correspondiente.

        Args:
            exportador (pd.Series): Columna de exportadores.

        Returns:
            pd.Series: Columna con los productos mapeados.
        """
        mapping = {
            'PBBPOLISUR SOCIEDAD DE RESPONS': 'POLIETILENO',
            'UNIPAR INDUPA SAIC': 'POLICLORURO DE VINILO',
            'COMPA?IA MEGA SOCIEDAD ANONIMA': 'GAS LICUADO',
            'COMPA?IA MOLINERA DEL SUR S. A': 'SEMOLA DE TRIGO',
            'TRANSPORTADORA DE GAS DEL SUR': 'GAS LICUADO',
            'VITERRA ARGENTINA S.A.': 'ACEITE / PELLETS / LECITINA',
            'LA NUEVA MANERA S.A.': 'HARINA DE TRIGO',
            'SYNGENTA': 'ACEITE',
            'LA NUEVA MANERA S.A.': 'HARINA DE TRIGO'
        }
        return exportador.map(mapping).fillna('INDETERMINADO')

def extraer_factura_y_orden(descripcion_mercancia: pd.Series) -> pd.DataFrame:
    """ Obtiene la factura y orden de la descripcion de mercancia

    Args:
        descripcion_mercancia (pd.Series): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # Definir las expresiones regulares
    regex_factura_proforma = re.compile(r'FACTURA\s+PROFORMA\s+(\d{6,})', re.IGNORECASE)
    regex_factura_nro = re.compile(r'FACTURA\s+NRO\.\s+([A-Z0-9-]{10,})', re.IGNORECASE)
    regex_factura_exportacion = re.compile(r'FACTURA\s+(?:DE\s+)?EXPORTACION(?:\s+E)?\s+([0-9]{4,5}-[A-Z0-9]{8})', re.IGNORECASE)
    regex_fact_de_exp = re.compile(r'FACT(?:\.|URA)?\.?DE\.?EXP\.?\s*([0-9]{4}-[0-9]{8})', re.IGNORECASE)
    regex_factura_simple = re.compile(r'\b([0-9]{4}-[0-9]{8})\b')
    regex_orden = re.compile(r'ORDEN\s+(\d{9,10})', re.IGNORECASE)

    resultados = []

    for desc in descripcion_mercancia:
        if not isinstance(desc, str):
            resultados.append({'FACTURA Nº': '', 'ORDEN': ''})
            continue

        desc_upper = desc.upper()
        desc_upper = re.sub(r'SHIPMENT\s*:\s*\d+', '', desc_upper)

        factura = ''
        orden = ''
        
        # Buscar FACTURA PROFORMA
        if match := regex_factura_proforma.search(desc_upper):
            factura = match.group(1)  
            orden = match.group(1)
        else:
            match_orden = regex_orden.search(desc_upper)
            if match_orden:
                orden = match_orden.group(1)
            if match := regex_factura_exportacion.search(desc_upper):
                factura = match.group(1)
            else:
                if match := regex_factura_nro.search(desc_upper):
                    factura = match.group(1)
                else:
                    if match := regex_fact_de_exp.search(desc_upper):
                        factura = match.group(1)
                    else:
                        if match := regex_factura_simple.search(desc_upper):
                            factura = match.group(1)
        resultados.append({'FACTURA Nº': factura, 'ORDEN': orden})

    return pd.DataFrame(resultados)

def agregar_factura_y_orden(df: pd.DataFrame) -> pd.DataFrame:
    """
        Toma un DataFrame, elimina la columna 'descripcion_mercancia',
        extrae las columnas 'FACTURA Nº' y 'ORDEN' usando la función extraer_factura_y_orden,
        y las inserta en el DataFrame.

        Args:
            df (pd.DataFrame): DataFrame original.

        Returns:
            pd.DataFrame: DataFrame modificado con las columnas 'FACTURA Nº' y 'ORDEN'.
    """
    # Extraer 'FACTURA Nº' y 'ORDEN' de 'descripcion_mercancia'
    factura_orden_df = extraer_factura_y_orden(df['descripcion_mercancia'])
        
    # Eliminar la columna 'descripcion_mercancia'
    df = df.drop(columns=['descripcion_mercancia'])
        
        # Concatenar el DataFrame original con las nuevas columnas
    df = pd.concat([df, factura_orden_df], axis=1)
        
    return df

def transform_campo9(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma la columna 'TRANSPORTE CAMPO 9' del DataFrame.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        pd.DataFrame: DataFrame modificado.
    """
    df['TRANSPORTE CAMPO 9'] = df['TRANSPORTE CAMPO 9'].str.replace('\n', '', regex=True)# Compilar el patrón regex
    patron = re.compile(r'(?: & -|-).*', re.IGNORECASE)

    df['TRANSPORTE CAMPO 9'] = df['TRANSPORTE CAMPO 9'].str.replace(patron, '', regex=True).str.strip()
    return df

if __name__ == "__main__":
    archivos = listar_archivos_pdf('C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/testing-data')
    