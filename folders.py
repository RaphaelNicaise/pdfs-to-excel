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