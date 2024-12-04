import os
from datetime import datetime
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

from app.services.EmailService import enviar_email


load_dotenv()
HIBP_API_KEY = os.getenv("HIBP_API_KEY")

if not HIBP_API_KEY:
    raise RuntimeError("Chave de API não configurada corretamente!")

HEADERS = {
    "HIBP-API-Key": HIBP_API_KEY,
    "User-Agent": "Osint Cyber",
}

API_URL_TEMPLATE = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"



async def notificar_vazamento_usuario_por_email_demonstrativo(email_usuario: str, titulo_vazamento: str, data: str,
                                                              descricao: str, image_uri: str):
    mensagem_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notificação de Vazamento</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .content {{
                margin: 20px 0;
                font-size: 16px;
                line-height: 1.6;
            }}
            .content a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            .image-container {{
                text-align: center;
                margin: 20px 0;
            }}
            .image-container img {{
                width: 80%;
                max-width: 500px;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .footer {{
                text-align: center;
                font-size: 14px;
                color: #888888;
                margin-top: 30px;
            }}
            .button {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                text-align: center;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
            .note {{
                font-size: 14px;
                color: #888888;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Alerta de Vazamento de Dados</h2>
            </div>
            <div class="content">
                <p>Olá Corno,</p>
                <p>Um novo vazamento foi identificado relacionado ao seu e-mail:</p>
                <p><strong>Título:</strong> {titulo_vazamento}</p>
                <p><strong>Data:</strong> {data}</p>
                <p><strong>Descrição:</strong> {descricao}</p>

                <!-- Exibe a imagem do vazamento -->
                <div class="image-container">
                    <img src="{image_uri}" alt="Imagem do Vazamento">
                </div>

                <p>Recomendamos que altere suas senhas imediatamente e esteja atento a possíveis fraudes.</p>
            </div>
            <div class="footer">
                <p>Atenciosamente,</p>
                <p><strong>Equipe de Segurança Start Osinc Sec - SOS</strong></p>
                <p class="note">Se você não reconhece esse e-mail, por favor, ignore ou entre em contato conosco.</p>
            </div>
        </div>
    </body>
    </html>
    """

    assunto = f"Novo vazamento detectado: {titulo_vazamento}"
    await enviar_email(email_usuario, assunto, mensagem_html)


def processar_vazamento(vazamento_data: dict) -> dict:
    """
    Processa os dados de um vazamento para o formato do banco de dados.
    Faz conversões de data e atribuições de valores padrão.
    """
    return {
        "nome": vazamento_data.get("Name"),
        "titulo": vazamento_data.get("Title", ""),
        "dominio_url": vazamento_data.get("Domain", ""),
        "data_vazamento": datetime.strptime(vazamento_data.get("BreachDate", ""), "%Y-%m-%d").date()
        if vazamento_data.get("BreachDate")
        else None,
        "data_adicao": datetime.utcnow(),  # Preenche com a data atual
        "data_atualizacao": datetime.strptime(vazamento_data.get("ModifiedDate", ""), "%Y-%m-%dT%H:%M:%SZ")
        if vazamento_data.get("ModifiedDate")
        else None,
        "descricao": vazamento_data.get("Description", None),
        "image_uri": vazamento_data.get("LogoPath", None),
        "pwn_count": vazamento_data.get("PwnCount", 0),
        "data_classes": vazamento_data.get("DataClasses", []),
    }


async def buscar_vazamentos_na_api(email: str) -> Optional[list[dict]]:
    """
    Faz uma requisição à API Have I Been Pwned para buscar vazamentos por e-mail.
    Lança exceções personalizadas para erros conhecidos.
    """
    url = API_URL_TEMPLATE.format(email=email)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    try:
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Nenhum vazamento foi encontrado para este e-mail.")
        else:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro na requisição para a API externa: {e.response.text}",
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar à API externa: {str(e)}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Erro ao processar a resposta da API externa. Não é um JSON válido.")