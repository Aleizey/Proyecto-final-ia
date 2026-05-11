from langchain_core.tools import tool
from fpdf import FPDF
import os
from datetime import datetime

@tool
def generar_pdf_presupuesto(contenido: str, nombre_archivo: str = "presupuesto.pdf"):
    """
    Genera un archivo PDF a partir de un texto proporcionado.
    Usala para crear presupuestos, informes o documentos formales para el cliente.
    """
    try:
        contenido = contenido.replace('\u20ac', 'EUR').replace('\u00b0', 'o')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)

        pdf.cell(190, 10, txt="PRESUPUESTO FORMAL", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 10, txt=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, txt=contenido)

        output_dir = "presupuestos"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ruta_final = os.path.join(output_dir, nombre_archivo)

        pdf.output(ruta_final)

        return f"PDF generado con exito en: {ruta_final}"

    except Exception as e:
        return f"Error al generar el PDF: {str(e)}"
