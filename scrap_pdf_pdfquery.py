from pdfquery import PDFQuery
import os 

def listar_archivos(directorio):
    archivos = []
    for file in os.listdir(directorio):
        if os.path.isfile(os.path.join(directorio, file)):
            archivos.append(file)
    return archivos


def obtener_fecha_emision(pdf: PDFQuery) -> str:
    """Obtiene la fecha de emision del archivo PDF usando pdfquery.
    """
    fecha_emision_xml = pdf.pq('LTTextLineHorizontal:contains("Fecha Emision")').next()
    return fecha_emision_xml.text()


for archivo in listar_archivos("testing-data/"):
    pdf = PDFQuery(f"testing-data/{archivo}")
    pdf.load(0)
    print(obtener_fecha_emision(pdf))