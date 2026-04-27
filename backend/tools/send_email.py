import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import tool

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

@tool
def send_email_tool(destinatario: str, asunto: str, cuerpo: str, ruta_pdf: str = None) -> str:
    """
    Envía un correo electrónico profesional al cliente. 
    Puede adjuntar un archivo PDF (como un presupuesto) si se proporciona la ruta.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMITENTE
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))

        if ruta_pdf and os.path.exists(ruta_pdf):
            with open(ruta_pdf, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(ruta_pdf)}")
                msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return f"Email enviado con éxito a {destinatario}."
    except Exception as e:
        return f"Error al enviar el email: {str(e)}"