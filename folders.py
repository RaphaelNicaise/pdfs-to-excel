import os
import shutil

def create_structure(path_carpeta: str, anio: str)-> None:
    """Crea una estructura de carpetas para almacenar archivos de un año con sus meses
    Args:
        path_carpeta (str): path donde se guarda la carpeta (formato -> "C:/escritorio/carpeta/")
        anio (int): nombre de la carpeta
    """
    if check_carpeta_existe(path_carpeta, anio):
        print(f"La carpeta {anio} ya existe en {path_carpeta}.")
        return
    
    meses = ["01-Enero", "02-Febrero", "03-Marzo", "04-Abril", "05-Mayo", "06-Junio", "07-Julio", "08-Agosto", "09-Septiembre", "10-Octubre", "11-Noviembre", "12-Diciembre"]
    anio_path = os.path.join(path_carpeta, str(anio))
    os.makedirs(anio_path, exist_ok=True)
    
    for mes in meses:
        mes_path = os.path.join(anio_path, mes)
        os.makedirs(mes_path, exist_ok=True)
        

def check_carpeta_existe(path_carpeta: str, anio: str) -> bool:
        """Verifica si en un path específico no existe una carpeta con un nombre dado
        Args:
            path_carpeta (str): Path donde se busca la carpeta
            anio (str): Nombre de la carpeta a verificar
        Returns:
            bool: True si la carpeta existe, False en caso contrario.
        """
        folder_path = os.path.join(path_carpeta, str(anio))
        return os.path.exists(folder_path) and os.path.isdir(folder_path)       
    
def remover_carpeta(path_carpeta: str, anio: str) -> None: 
    """Elimina una carpeta y su contenido
    Args:
        path_carpeta (str): Path donde se busca la carpeta
        anio (str): Nombre de la carpeta a eliminar
    """
    
    if check_carpeta_existe(path_carpeta, anio):
        shutil.rmtree(os.path.join(path_carpeta, str(anio)), ignore_errors=True)
        print(f"Carpeta {anio} eliminada en {path_carpeta}.")
    else:
        print(f"La carpeta {anio} no existe en {path_carpeta}.") 

def obtener_path_mes(path_carpeta: str, anio: str, mes: str) -> str:
        """Devuelve el path de la carpeta de un mes y año específico
        Args:
            path_carpeta (str): Path donde se encuentra la estructura de carpetas
            anio (str): Año de la carpeta
            mes (str): Mes de la carpeta (formato -> "01-Enero")
        Returns:
            str: Path completo de la carpeta del mes y año especificado
        """
        mes_path = os.path.join(path_carpeta, str(anio), mes)
        if os.path.exists(mes_path) and os.path.isdir(mes_path):
            return mes_path
        else:
            raise FileNotFoundError(f"La carpeta del mes {mes} en el año {anio} no existe en {path_carpeta}.")

def main():
    # create_structure("C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/carpetas", 2025)
    # remover_carpeta("C:/Users/Usuario/Desktop/Rapha/pdfs-to-excel/carpetas", 2025)
    pass

if __name__ == "__main__":
    main() 