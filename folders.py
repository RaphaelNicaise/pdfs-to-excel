import os
import shutil

def create_folders_empresas(folder_path: str, empresas: list[str])-> None:
    """_summary_

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
    ...
    
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