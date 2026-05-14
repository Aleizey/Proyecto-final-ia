import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from datetime import datetime

from langchain_core.tools import tool

load_dotenv()

def get_latest_presupuesto():
    """Obtiene el PDF de presupuesto más reciente"""
    presupuestos_dir = "presupuestos"
    if not os.path.exists(presupuestos_dir):
        return None
    
    files = [f for f in os.listdir(presupuestos_dir) if f.endswith('.pdf')]
    if not files:
        return None
    
    files_with_time = [(f, os.path.getmtime(os.path.join(presupuestos_dir, f))) for f in files]
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    return os.path.join(presupuestos_dir, files_with_time[0][0])

def log_email_debug(msg: str):
    """Log para debugging"""
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "email_debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"[{datetime.now()}] {msg}\n")
    except:
        pass

@tool
def enviar_email_presupuesto(destinatario: str) -> str:
    """
    ENVIAR PRESUPUESTO POR EMAIL. Usa esta herramienta cuando el usuario pida enviar un presupuesto por correo electrónico.
    El parámetro 'destinatario' es la dirección de email del cliente. Se adjunta automáticamente el último PDF de presupuesto generado.
    Ejemplo: enviar_email_presupuesto(destinatario="cliente@gmail.com")
    """
    log_email_debug(f"enviar_email_presupuesto LLAMADA - destinatario={destinatario}")
    
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        load_dotenv(env_path)
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        email_remitente = os.getenv("EMAIL_REMITENTE")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        log_email_debug(f"destinatario={destinatario}, smtp_server={smtp_server}, email_remitente={email_remitente}, has_password={bool(email_password)}")
        
        if not email_remitente or not email_password:
            return f"Error: Configuración de email incompleta. Verifica SMTP_SERVER, EMAIL_REMITENTE y EMAIL_PASSWORD en .env (server={smtp_server}, remitente={email_remitente})"
        
        msg = MIMEMultipart()
        msg['From'] = email_remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Presupuesto MARAUDIO - Sonido e Iluminación Profesional"
        
        cuerpo = f"""Hola,

Adjunto encontrarás el presupuesto de MARAUDIO para tu evento de sonido e iluminación.

Si tienes alguna pregunta, no dudes en contactarnos.

Un saludo,
MARAUDIO
Soporte Técnico Profesional"""
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        ruta_pdf = get_latest_presupuesto()
        
        if ruta_pdf and os.path.exists(ruta_pdf):
            with open(ruta_pdf, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                filename = os.path.basename(ruta_pdf)
                part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(part)
            attachment_info = f" con adjunto {os.path.basename(ruta_pdf)}"
        else:
            attachment_info = " (sin adjunto PDF)"
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_remitente, email_password)
        server.send_message(msg)
        server.quit()
        
        return f"Email enviado con éxito a {destinatario}{attachment_info}"
    
    except Exception as e:
        log_email_debug(f"Error - {str(e)}")
        return f"Error al enviar el email: {str(e)}"