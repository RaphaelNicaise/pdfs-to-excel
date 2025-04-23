from pdfquery import PDFQuery
import os 

# fecha_emision

def get_datos_from_pdf(pdf: PDFQuery) -> dict:
    """Obtiene los datos del archivo PDF usando pdfquery.
    """
     
    datos = {
        "fecha_emision": obtener_fecha_emision(pdf),
        "porteador": get_porteador(pdf),
        "ciudad_pais_partida": get_ciudad_pais_partida(pdf),
        "ciudad_pais_destino": get_ciudad_pais_destino(pdf),
        "camion_original": get_camion_original(pdf),
        "placa_camion": get_placa_camion(pdf),
        "placa_semiremolque": get_placa_semiremolque(pdf),
        "carta_porte": get_carta_porte(pdf),
        "aduana_destino": get_aduana_destino(pdf),
        "destinatario": get_destinatario(pdf),
        "valor_FOT": get_valor_FOT(pdf),
        "flete_usd": get_flete_usd(pdf),
        "consignatario": get_consignatario(pdf),
        "tipo_bultos": get_tipo_bultos(pdf),
        "cantidad_bultos": get_cantidad_bultos(pdf),
        "peso_bruto": get_peso_bruto(pdf),
        "documentos_anexos": get_documentos_anexos(pdf),
        "descripcion_mercancia": get_descripcion_mercancia(pdf), # falta cortar
        "conductor": get_conductor(pdf)
    }
    return datos

# archivo
def get_archivo_nombre(pdf: PDFQuery) -> str:
    """
    Extrae el nombre del archivo PDF.
    """
    nombre = pdf.pq('LTTextLineHorizontal:contains("N°")').next()
    return nombre.text()

def obtener_fecha_emision(pdf: PDFQuery) -> str:
    """Obtiene la fecha de emision del archivo PDF usando pdfquery.
    """
    fecha_emision_xml = pdf.pq('LTTextLineHorizontal:contains("Fecha Emision")').next()
    return fecha_emision_xml.text()

# porteador

def get_porteador(pdf) -> str:
    """Obtiene el nombre y domicilio del porteador del archivo PDF usando pdfquery.
    """
    base = pdf.pq('LTTextLineHorizontal:contains("Nombre y domicilio del porteador")')
    if not base:
        return ""
    siguiente = base.next()
    texto = siguiente.text().strip() if siguiente is not None else ""
        
    if texto == "/ Nome e endereco do transportador":
        siguiente = siguiente.next()
        texto = siguiente.text().strip() if siguiente is not None else ""

    return texto

# ciudad_pais_partida

def get_ciudad_pais_partida(pdf: PDFQuery) -> str:
    """Obtiene la ciudad de partida del archivo PDF usando pdfquery.
    """
    ciudad_partida_xml = pdf.pq('LTTextLineHorizontal:contains("Aduana, ciudad y pais de partida")').next()
    return ciudad_partida_xml.text()

# ciudad_pais_destino

def get_ciudad_pais_destino(pdf: PDFQuery) -> str:
    """Obtiene la ciudad de destino del archivo PDF usando pdfquery.
    """
    ciudad_destino_xml = pdf.pq('LTTextLineHorizontal:contains("/ Cidade e pais de destino final")').next()
    return ciudad_destino_xml.text()

# camion_original

def get_camion_original(pdf: PDFQuery) -> str:
    """Obtiene el camion original del archivo PDF usando pdfquery.
    """
    x0, y0, x1, y1 = 31.52, 634.96, 306.04, 693.48

    text_elements = pdf.pq(f'LTTextLineHorizontal:in_bbox("{x0},{y0},{x1},{y1}")')
    return text_elements.text().split("proprietario", 1)[-1].strip()

# placa_camion

def get_placa_camion(pdf: PDFQuery) -> str:
    """
    Obtiene la placa del camión del archivo PDF usando pdfquery.
    """

    placa_camion_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Placa de Camion")').next()
    return placa_camion_xml.text().strip()

# placa_semiremolque
def get_placa_semiremolque(pdf: PDFQuery)->str:
    """
    Obtiene la placa del semiremolque del archivo PDF usando pdfquery.
    """
    placa_semiremolque_xml = pdf.pq(f'LTTextLineHorizontal:contains("Placa:")').next()
    return placa_semiremolque_xml.text().strip()

# carta_de_porte
def get_carta_porte(pdf: PDFQuery) -> str:
    """
    Obtiene la carta de porte del archivo PDF usando pdfquery.
    """
    carta_porte_xml = pdf.pq(f'LTTextLineHorizontal:contains("23 N? carta de porte")').next().next()
    return carta_porte_xml.text().strip()

# aduana_destino
def get_aduana_destino(pdf: PDFQuery) -> str:
    """
    Obtiene la aduana de destino del archivo PDF usando pdfquery.
    """
    aduana_destino_xml = pdf.pq(f'LTTextLineHorizontal:contains("24 Aduana de destino/ Alfandega de destino")').next()
    return aduana_destino_xml.text().strip()

# destinatario

def get_destinatario(pdf: PDFQuery) -> str:
    """
    Obtiene el destinatario del archivo PDF usando pdfquery.
    """
    destinatario_xml = pdf.pq(f'LTTextLineHorizontal:contains("34 Destinatario / Destinatario")').next()
    return destinatario_xml.text().replace('\n', '').strip()

# valor_FOT

def get_valor_FOT(pdf: PDFQuery) ->str:
    """
    Obtiene el valor FOT del archivo PDF usando pdfquery.
    """
    valor_FOT_xml = pdf.pq(f'LTTextLineHorizontal:contains("/Valor FOT")').next()
    return valor_FOT_xml.text().strip()

# flete_usd

def get_flete_usd(pdf: PDFQuery) -> str:
    """
    Obtiene el flete en USD del archivo PDF usando pdfquery.
    """
    flete_usd_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Frete em U$S")').next()
    return flete_usd_xml.text().strip()

# consignatario

def get_consignatario(pdf: PDFQuery) -> str:
    """
    Obtiene el consignatario del archivo PDF usando pdfquery.
    """
    consignatario_xml = pdf.pq(f'LTTextLineHorizontal:contains("35 Consignatario /Consignatario ")').next()
    return consignatario_xml.text().replace('\n', '').strip()

# tipo_bultos

def get_tipo_bultos(pdf: PDFQuery) -> str:
    """
    Obtiene el tipo de bultos del archivo PDF usando pdfquery.
    """
    tipo_bultos_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Tipo dos volumes")').next()
    return tipo_bultos_xml.text().strip()

# cantidad_bultos
def get_cantidad_bultos(pdf: PDFQuery) -> str:
    """
    Obtiene la cantidad de bultos del archivo PDF usando pdfquery.
    """

    
    cantidad_bultos_xml = pdf.pq(f'LTTextBoxHorizontal:contains("31 Cantidad de bultos ")').next()
    return cantidad_bultos_xml.text().strip()

# peso_bruto

def get_peso_bruto(pdf: PDFQuery) -> str:

    """
    Obtiene el peso bruto del archivo PDF usando pdfquery.
    """
    peso_bruto_xml = pdf.pq(f'LTTextBoxHorizontal:contains("Peso bruto")').next()
    return peso_bruto_xml.text().strip()

# documentos_anexos

def get_documentos_anexos(pdf: PDFQuery) -> str:
    """
    Obtiene los documentos anexos del archivo PDF usando pdfquery.
    """
    documentos_anexos_xml = pdf.pq(f'LTTextLineHorizontal:contains("Documentos anexos")').next()
    return documentos_anexos_xml.text().strip()

# descripcion_mercancia

def get_descripcion_mercancia(pdf: PDFQuery) -> str:
    """
    Obtiene la descripcion de la mercancia del archivo PDF usando pdfquery.
    """
    descripcion_mercancia_xml = pdf.pq(f'LTTextLineHorizontal:contains("/ Marcas e numeros dos volumes, descric?o das mercadorias")').next()
    return descripcion_mercancia_xml.text().strip()

# conductor

def get_conductor(pdf: PDFQuery) -> str:
    """
    Obtiene el nombre del conductor del archivo PDF usando pdfquery.
    """
    conductor_xml = pdf.pq(f'LTTextLineHorizontal:contains("CONDUCTOR 1")')
    return conductor_xml.text().strip()

