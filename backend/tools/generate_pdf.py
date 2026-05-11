from langchain_core.tools import tool
from fpdf import FPDF
import os
from datetime import datetime

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "agent", "maraudio_logo.png")

@tool
def generar_pdf_presupuesto(
    contenido: str,
    nombre_archivo: str = None,
    cliente: str = None,
    evento: str = None,
    fecha_evento: str = None,
    telefono: str = None,
    email: str = None
):
    """
    Genera un PDF de presupuesto profesional con diseño elaborado.
    
    Parameters:
    - contenido: Texto del presupuesto (puede incluir items con precios)
    - nombre_archivo: Nombre del archivo PDF (default: presupuesto_YYYYMMDD_HHMMSS.pdf)
    - cliente: Nombre del cliente (opcional)
    - evento: Tipo de evento (opcional)
    - fecha_evento: Fecha del evento (opcional)
    - telefono: Teléfono de contacto (opcional)
    - email: Email de contacto (opcional)
    
    El contenido puede incluir listas de equipos en formato libre.
    El tool extraera automaticamente items con precios si siguen formatos como:
    - "Altavoz x2 - 100 EUR"
    - "- Mesa de mezclas: 50 EUR/dia"
    - "Servicio DJ: 200 EUR"
    """
    try:
        contenido = contenido.replace('\u20ac', 'EUR').replace('\u00b0', 'o')
        
        if nombre_archivo is None:
            nombre_archivo = f"presupuesto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf'
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Colores de la empresa
        PRIMARY_COLOR = (138, 43, 226)  # Púrpura
        SECONDARY_COLOR = (56, 189, 248)  # Cyan/Azul claro
        DARK_BG = (15, 15, 25)  # Fondo oscuro
        
        # ===== HEADER CON LOGO =====
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=10, y=8, w=30)
        
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(*PRIMARY_COLOR)
        pdf.cell(0, 15, txt="MARAUDIO", ln=True, align="R")
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, txt="Soporte Tecnico Profesional", ln=True, align="R")
        pdf.cell(0, 6, txt="Eventos de Sonido e Iluminacion", ln=True, align="R")
        
        pdf.ln(5)
        
        # ===== LINEA DECORATIVA =====
        pdf.set_draw_color(*PRIMARY_COLOR)
        pdf.set_line_width(2)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
        
        # ===== TITULO =====
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, txt="PRESUPUESTO", ln=True, align="C")
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, txt=f"Nº {datetime.now().strftime('%Y%m%d%H%M%S')}", ln=True, align="C")
        pdf.ln(8)
        
        # ===== DATOS DEL CLIENTE =====
        if cliente or evento or fecha_evento:
            pdf.set_fill_color(245, 245, 250)
            pdf.set_draw_color(200, 200, 210)
            pdf.rect(10, pdf.get_y(), 190, 35, 'D')
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(*PRIMARY_COLOR)
            pdf.cell(95, 8, txt="DATOS DEL CLIENTE", border=0, ln=0)
            pdf.cell(95, 8, txt="DATOS DEL EVENTO", border=0, ln=True)
            
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(50, 50, 50)
            
            y_start = pdf.get_y()
            
            # Cliente info (left column)
            if cliente:
                pdf.cell(95, 6, txt=f"Cliente: {cliente}", border=0, ln=True)
            if telefono:
                pdf.cell(95, 6, txt=f"Telefono: {telefono}", border=0, ln=True)
            if email:
                pdf.cell(95, 6, txt=f"Email: {email}", border=0, ln=True)
            
            pdf.set_xy(105, y_start)
            
            # Evento info (right column)
            if evento:
                pdf.cell(95, 6, txt=f"Evento: {evento}", border=0, ln=True)
            if fecha_evento:
                pdf.cell(95, 6, txt=f"Fecha: {fecha_evento}", border=0, ln=True)
            
            pdf.ln(5)
        
        # ===== TABLA DE EQUIPOS/SERVICIOS =====
        pdf.ln(5)
        
        # Headers de la tabla
        pdf.set_fill_color(*PRIMARY_COLOR)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(10, 10, txt="#", border=1, fill=True, align="C")
        pdf.cell(80, 10, txt="Descripcion", border=1, fill=True, align="C")
        pdf.cell(25, 10, txt="Cant.", border=1, fill=True, align="C")
        pdf.cell(35, 10, txt="Precio Ud.", border=1, fill=True, align="C")
        pdf.cell(40, 10, txt="Total", border=1, fill=True, align="C")
        pdf.ln()
        
        # Parsear contenido para extraer items
        items = parsear_items(contenido)
        
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(50, 50, 50)
        
        total_general = 0
        fill = False
        
        for i, item in enumerate(items, 1):
            item_total = item.get('total', item.get('precio', 0))
            total_general += item_total
            
            bg = (248, 248, 252) if fill else (255, 255, 255)
            pdf.set_fill_color(*bg)
            
            pdf.cell(10, 8, txt=str(i), border=1, fill=True, align="C")
            pdf.cell(80, 8, txt=item.get('descripcion', '')[:40], border=1, fill=True)
            pdf.cell(25, 8, txt=str(item.get('cantidad', 1)), border=1, fill=True, align="C")
            pdf.cell(35, 8, txt=f"{item.get('precio', 0):.2f} EUR", border=1, fill=True, align="C")
            pdf.cell(40, 8, txt=f"{item_total:.2f} EUR", border=1, fill=True, align="C")
            pdf.ln()
            
            fill = not fill
        
        # Si no hay items parseados, mostrar contenido como texto
        if not items:
            pdf.set_font("Arial", size=9)
            pdf.multi_cell(190, 6, txt=contenido[:500], border=1)
        
        pdf.ln(5)
        
        # ===== TOTALES =====
        pdf.set_x(130)
        pdf.set_font("Arial", size=10)
        pdf.cell(30, 8, txt="Subtotal:", border=0, align="R")
        pdf.cell(30, 8, txt=f"{total_general:.2f} EUR", border=0, align="R", ln=True)
        
        pdf.set_x(130)
        pdf.cell(30, 8, txt="IVA (21%):", border=0, align="R")
        iva = total_general * 0.21
        pdf.cell(30, 8, txt=f"{iva:.2f} EUR", border=0, align="R", ln=True)
        
        pdf.set_x(130)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(*PRIMARY_COLOR)
        pdf.cell(30, 10, txt="TOTAL:", border=0, align="R")
        total_con_iva = total_general + iva
        pdf.cell(30, 10, txt=f"{total_con_iva:.2f} EUR", border=0, align="R", ln=True)
        
        # ===== CONDICIONES =====
        pdf.ln(15)
        pdf.set_draw_color(*PRIMARY_COLOR)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 6, txt="Condiciones:", ln=True)
        
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(100, 100, 100)
        condiciones = [
            "- Precios sin IVA incluido",
            "- Validez del presupuesto: 15 dias",
            "- Se requiere senal del 30% para confirmar reserva",
            "- El equipo incluye tecnico de sonido durante el evento",
            "- Montaje y desmontaje incluido en el precio"
        ]
        for cond in condiciones:
            pdf.cell(0, 5, txt=cond, ln=True)
        
        # ===== FOOTER =====
        pdf.ln(10)
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, txt="MARAUDIO - Sonido e Iluminacion Profesional", ln=True, align="C")
        pdf.cell(0, 5, txt="info@maraudio.es | www.maraudio.es", ln=True, align="C")
        pdf.cell(0, 5, txt=f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", ln=True, align="C")
        
        output_dir = "presupuestos"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ruta_final = os.path.join(output_dir, nombre_archivo)
        pdf.output(ruta_final)
        
        return f"presupuesto_{nombre_archivo}"

    except Exception as e:
        return f"Error al generar el PDF: {str(e)}"


def parsear_items(texto):
    """Extrae items con precios del texto"""
    items = []
    
    lineas = texto.split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        
        # Patrones para detectar precios
        import re
        
        # "Altavoz x2 - 100 EUR" o "Altavoz x2: 100 EUR"
        match = re.search(r'(.+?)[x×](\d+)\s*[-:]\s*(\d+(?:[.,]\d+)?)\s*(?:EUR|€|e)', linea, re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            cantidad = int(match.group(2))
            precio = float(match.group(3).replace(',', '.'))
            items.append({
                'descripcion': desc,
                'cantidad': cantidad,
                'precio': precio,
                'total': cantidad * precio
            })
            continue
        
        # "Altavoz 100 EUR" (sin cantidad)
        match = re.search(r'(.+?)\s+(\d+(?:[.,]\d+)?)\s*(?:EUR|€|e)\b', linea, re.IGNORECASE)
        if match and len(linea) < 60:
            desc = match.group(1).strip()
            precio = float(match.group(2).replace(',', '.'))
            if desc and precio > 0:
                items.append({
                    'descripcion': desc,
                    'cantidad': 1,
                    'precio': precio,
                    'total': precio
                })
        
        # "Servicio DJ - 200" (con guion)
        match = re.search(r'[-–]\s*(\d+(?:[.,]\d+)?)\s*(?:EUR|€)?\s*$', linea)
        if match:
            precio = float(match.group(1).replace(',', '.'))
            if precio > 0 and len(linea) < 50:
                desc = re.sub(r'\s*-\s*\d+.*$', '', linea).strip()
                if desc:
                    items.append({
                        'descripcion': desc,
                        'cantidad': 1,
                        'precio': precio,
                        'total': precio
                    })
    
    return items