
import os 
import re

from pdfquery import PDFQuery
import fitz

# fecha_emision
def check_format(pdf: PDFQuery):
    """
    Verifica si el formato del PDF es correcto.


    Args:
        pdf (PDFQuery): instancia de PDFQuery del archivo PDF.
    """
    
    return bool(pdf.pq('LTTextLineHorizontal:contains("Manifiesto Internacional de Carga por Carretera / Declaracion de Transito Aduanero")'))
       
    
def get_datos_from_pdf(pdf: PDFQuery) -> dict:
    """Obtiene los datos del archivo PDF usando pdfquery.
    """
     
    datos = {
        "FECHA CARGA": obtener_FECHA_CARGA(pdf), # listo
        "C.R.T.": get_CRT(pdf), # listo
        "D.D.T": get_DDT(pdf), # listo
        #ORDEN
        #FACTURA Nº
        #EXPORTADOR (r/z de remitente)
        "DESTINATARIO": get_DESTINATARIO(pdf), # FALTA CORTAR DIRECCION SOLO (R/Z)
        "TRANSPORTE CAMPO 1": get_TRANSPORTE_CAMPO_1(pdf), # listo
        #NACIONALIDAD TRANSPORTE
        # TRANSPORTE CAMPO 9 (SE INGRESA DESPUES)
        "TRACTOR": get_TRACTOR(pdf), # listo
        "SEMI": get_SEMI(pdf), # listo 
        "DESTINO": get_DESTINO(pdf), # listo
        "ADUANA DESTINO": get_ADUANA_DESTINO(pdf), # listo
        #PRODUCTO
        "KILOS BRUTOS": get_PESO_BRUTO(pdf), # listo
        "VALOR FOB": get_VALOR_FOT(pdf), # listo
        "PRECINTO": get_PRECINTO(pdf),
        
        
        "descripcion_mercancia": get_descripcion_mercancia(pdf), # falta cortar para que se divida en ORDEN, FACTURA Y PRODUCTO (el producto lo saco con la logica)
    }
    return datos

# archivo
def get_archivo_nombre(pdf: PDFQuery) -> str:
    """
    Extrae el nombre del archivo PDF.
    """
    try:
        nombre = pdf.pq('LTTextLineHorizontal:contains("N°")').next()
        return nombre.text()
    except KeyError as e:
        print(f"Error: {e}")
        return ""

def obtener_FECHA_CARGA(pdf: PDFQuery) -> str:
    """Obtiene la fecha de emision del archivo PDF usando pdfquery.
    """
    try:
        fecha_emision_xml = pdf.pq('LTTextLineHorizontal:contains("Fecha Emision")').next()
        return fecha_emision_xml.text()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
# porteador

def get_TRANSPORTE_CAMPO_1(pdf) -> str:
    """Obtiene el nombre y domicilio del porteador del archivo PDF usando pdfquery.
    """
    try:
        base = pdf.pq('LTTextLineHorizontal:contains("Nombre y domicilio del porteador")')
        if not base:
            return ""
        siguiente = base.next()
        texto = siguiente.text().strip() if siguiente is not None else ""
            
        if texto == "/ Nome e endereco do transportador":
            siguiente = siguiente.next()
            texto = siguiente.text().strip() if siguiente is not None else ""

        return texto
    except KeyError as e:
        print(f"Error: {e}")
        return ""
# ciudad_pais_partida

# def get_ciudad_pais_partida(pdf: PDFQuery) -> str:
#     """Obtiene la ciudad de partida del archivo PDF usando pdfquery.
#     """
#     try:
#         ciudad_partida_xml = pdf.pq('LTTextLineHorizontal:contains("Aduana, ciudad y pais de partida")').next()
#         return ciudad_partida_xml.text()
#     except KeyError as e:
#         print(f"Error: {e}")
#         return ""

# ciudad_pais_destino

def get_DESTINO(pdf: PDFQuery) -> str:
    """Obtiene la ciudad de destino del archivo PDF usando pdfquery.
    """
    try:
        ciudad_destino_xml = pdf.pq('LTTextLineHorizontal:contains("/ Cidade e pais de destino final")').next()
        return ciudad_destino_xml.text()
    except KeyError as e:
        print(f"Error: {e}")
        return ""


# placa_camion

def get_TRACTOR(pdf: PDFQuery) -> str:
    """
    Obtiene la placa del camión del archivo PDF usando pdfquery.
    """
    try:
        placa_camion_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Placa de Camion")').next()
        return placa_camion_xml.text().strip()
    except KeyError as e:
        print(f"Error: {e}")
        return ""

    

# placa_semiremolque
def get_SEMI(pdf: PDFQuery)->str:
    """
    Obtiene la placa del semiremolque del archivo PDF usando pdfquery.
    """
    
    try:
        placa_semiremolque_xml = pdf.pq(f'LTTextLineHorizontal:contains("Placa:")').next()
        return placa_semiremolque_xml.text().strip()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    

# carta_de_porte
def get_CRT(pdf: PDFQuery) -> str:
    """
    Obtiene la carta de porte del archivo PDF usando pdfquery.
    """
    try:
        carta_porte_xml = pdf.pq(f'LTTextLineHorizontal:contains("23 N? carta de porte")').next().next()
        return carta_porte_xml.text().strip()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
   

# aduana_destino
def get_ADUANA_DESTINO(pdf: PDFQuery) -> str:
    """
    Obtiene la aduana de destino del archivo PDF usando pdfquery.
    """
    try:
        aduana_destino_xml = pdf.pq(f'LTTextLineHorizontal:contains("24 Aduana de destino/ Alfandega de destino")').next()
        return aduana_destino_xml.text().strip()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
    

# destinatario

def get_DESTINATARIO(pdf: PDFQuery) -> str:
    """
    Obtiene el destinatario del archivo PDF usando pdfquery.
    """
    try:
        destinatario_xml = pdf.pq(f'LTTextLineHorizontal:contains("34 Destinatario / Destinatario")').next()
        return destinatario_xml.text().replace('\n', '').strip()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
    

# valor_FOT

def get_VALOR_FOT(pdf: PDFQuery) ->str:
    """
    Obtiene el valor FOT del archivo PDF usando pdfquery.
    """
    try:
        valor_FOT_xml = pdf.pq(f'LTTextLineHorizontal:contains("/Valor FOT")').next()
        return valor_FOT_xml.text().strip()

    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
    
# flete_usd

# def get_flete_usd(pdf: PDFQuery) -> str:
#     """
#     Obtiene el flete en USD del archivo PDF usando pdfquery.
#     """
    
#     try:
#         flete_usd_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Frete em U$S")').next()
#         return flete_usd_xml.text().strip()

#     except KeyError as e:
#         print(f"Error: {e}")
#         return ""
    
# consignatario

# def get_consignatario(pdf: PDFQuery) -> str:
#     """
#     Obtiene el consignatario del archivo PDF usando pdfquery.
#     """
    
#     try:
#         consignatario_xml = pdf.pq(f'LTTextLineHorizontal:contains("35 Consignatario /Consignatario ")').next()
#         return consignatario_xml.text().replace('\n', '').strip()

#     except KeyError as e:
#         print(f"Error: {e}")
#         return ""
    
# tipo_bultos

# def get_tipo_bultos(pdf: PDFQuery) -> str:
#     """
#     Obtiene el tipo de bultos del archivo PDF usando pdfquery.
#     """
    
#     try:
#         tipo_bultos_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Tipo dos volumes")').next()
#         return tipo_bultos_xml.text().strip()

#     except KeyError as e:
#         print(f"Error: {e}")
#         return ""
    
# # cantidad_bultos
# def get_cantidad_bultos(pdf: PDFQuery) -> str:
#     """
#     Obtiene la cantidad de bultos del archivo PDF usando pdfquery.
#     """
#     try:
#         cantidad_bultos_xml = pdf.pq(f'LTTextBoxHorizontal:contains("31 Cantidad de bultos ")').next()
#         return cantidad_bultos_xml.text().strip()

#     except KeyError as e:
#         print(f"Error: {e}")
#         return ""
    
    
# peso_bruto

def get_PESO_BRUTO(pdf: PDFQuery) -> str:

    """
    Obtiene el peso bruto del archivo PDF usando pdfquery.
    """
    
    try:
        peso_bruto_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Peso bruto")').next()
        return peso_bruto_xml.text().strip()

    except KeyError as e:
        print(f"Error: {e}")
        return ""

# documentos_anexos

def get_DDT(pdf: PDFQuery) -> str:
    """
    Obtiene los documentos anexos del archivo PDF usando pdfquery.
    """
    
    try:
        documentos_anexos_xml = pdf.pq(f'LTTextLineHorizontal:contains("Documentos anexos")').next()
        return documentos_anexos_xml.text().strip()

    except KeyError as e:
        print(f"Error: {e}")
        return ""

# descripcion_mercancia

def get_descripcion_mercancia(pdf: PDFQuery) -> str:
    """
    Obtiene la descripcion de la mercancia del archivo PDF usando pdfquery.
    """
    try:
        descripcion_mercancia_xml = pdf.pq(f'LTTextLineHorizontal:contains("/ Marcas e numeros dos volumes, descric?o das mercadorias")').next()
        return descripcion_mercancia_xml.text().strip()

    except KeyError as e:
        print(f"Error: {e}")
        return ""

# conductor

# def get_conductor(pdf: PDFQuery) -> str:
#     """
#     Obtiene el nombre del conductor del archivo PDF usando pdfquery.
#     """
    
#     try:
#         conductor_xml = pdf.pq(f'LTTextLineHorizontal:contains("CONDUCTOR 1")')
#         return conductor_xml.text().strip()
#     except KeyError as e:
#         print(f"Error al obtener el nombre del archivo: {e}")
#         return ""
    

# ESTE VA APARTE, EN EL TRANSFORM_DF,se hace despues 
def get_TRANSPORTE_CAMPO_9(archivos: list[str]):
    """_summary_

    Args:
        archivo (str): _description_

    Returns:
        _type_: _description_
    """
    
    data = []
    for archivo in archivos:
    
        pdf = fitz.open(archivo).load_page(0)
        # Load the page content as text
        page_text = pdf.get_text("text")

        texto_antes = 'CAMINH?O ORIGINAL : Nome e endereco do proprietario\n9\n'
        texto_despues = 'CAMION SUBSTITUTO : Nombre y domicilio del propietario'

        pattern = re.escape(texto_antes) + r"(.*?)" + re.escape(texto_despues)
        
        matches = re.findall(pattern, page_text, re.DOTALL)

        data.append(matches[0].split('- ')[0].strip()) if matches else None
    
    return data


# precinto
def get_PRECINTO(pdf: PDFQuery):
    """
    Obtiene el precinto del archivo PDF usando pdfquery.
    """
    try:
        text  =  pdf.pq('LTTextLineHorizontal:contains("37 Numero de los precintos")').next().text()
    except KeyError as e:
        print(f"Error: {e}")
        return ""
    
    return text