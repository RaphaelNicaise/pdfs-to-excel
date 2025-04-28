import os
import shutil
import re

import pandas as pd
from openpyxl import load_workbook

def create_folders_empresas(folder_path: str, empresas: list[str])-> None:
    """ Funcion que crea carpetas basado en lista de empresas

    Args:
        folder_path (str): _description_
        empresas (list[str]): _description_
    """
    
    
    for empresa in empresas:
        check_carpeta_existe(os.path.join(folder_path, empresa))
        empresa_path = os.path.join(folder_path, empresa)
        os.makedirs(empresa_path, exist_ok=True)
        

def create_structure_folders(folder_path: str, empresas: list[str])-> None:
    """Esta funcion deberia crear las carpetas por empresa dentro de una carpeta padre, aparte de los archivos de excel por empresa, y el AG general

    Args:
        folder_path (str): _description_
        empresas (list[str]): _description_
    """
    
def integrate_files(destino: str, df)-> None:
    """ Esta funcion crea las carpetas por empresa dentro de una carpeta elegida en destino, y adentro de cada carpeta va el df filtrado por empresa, y por fuera el df general

    Args:
        folder_path (str): _description_
        empresas (list[str]): _description_
        df (_type_): _description_
    os.makedirs(destino, exist_ok=True)
    """
    
    # Save the general dataframe
    general_excel_path = os.path.join(destino, "AG.xlsx")
    df.to_excel(general_excel_path, index=False)
    acomodar_columnas(general_excel_path)
    
    empresas = list(set(df["TRANSPORTE CAMPO 1"])) # set para no tener repetidos y convierte a lista

    for empresa in empresas:
        nombre_empresa_formateado = re.sub(r'[/:*?"<>|]', '', empresa).strip()
        empresa_folder = os.path.join(destino, nombre_empresa_formateado)
        os.makedirs(empresa_folder, exist_ok=True)
        
        df_empresa = df[df['TRANSPORTE CAMPO 1'] == empresa]
        
        empresa_excel_path = os.path.join(empresa_folder, f"AG-{nombre_empresa_formateado}.xlsx")
        df_empresa.to_excel(empresa_excel_path, index=False)
        acomodar_columnas(empresa_excel_path) # acomoda las columnas de cada archivo
    
    
    
def acomodar_columnas(path_excel):
    workbook = load_workbook(path_excel)
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

    workbook.save(path_excel)
    workbook.close()
        
    
def check_carpeta_existe(folder_path: str) -> bool:
    """_summary_

    Args:
        folder_path (str): _description_

    Returns:
        bool: _description_
    """
    return os.path.exists(folder_path) and os.path.isdir(folder_path)       

def main():
    empresas = ["empresa1assad", "empresaasdads2", "empresa3adsdad"]
    folder_path = 'C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/data'
    create_folders_empresas(folder_path, empresas)
    ...
if __name__ == "__main__":
    main() 