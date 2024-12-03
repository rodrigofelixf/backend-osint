import aiosmtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv
import os

from fastapi import HTTPException

load_dotenv()


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

async def enviar_email(destinatario: str, assunto: str, mensagem_html: str):
    email = EmailMessage()
    email["From"] = f"Start Osint Sec - SOS <{SMTP_USERNAME}>"
    email["To"] = destinatario
    email["Subject"] = assunto

    # Define o conteúdo do e-mail como HTML
    email.set_content(mensagem_html, subtype="html")

    try:
        await aiosmtplib.send(
            email,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True
        )
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")
