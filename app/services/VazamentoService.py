from typing import Optional
import httpx
import os
from fastapi import HTTPException
from datetime import datetime
from dotenv import load_dotenv
from app.models.vazamentos import models, schemas
from sqlalchemy.orm import Session
from app.services import UsuarioService
from app.services.EmailService import enviar_email
import json

load_dotenv()
HIBP_API_KEY = os.getenv("HIBP_API_KEY")

if not HIBP_API_KEY:
    raise RuntimeError("Chave de API não configurada corretamente!")

HEADERS = {
    "HIBP-API-Key": HIBP_API_KEY,
    "User-Agent": "Osint Cyber",
}

API_URL_TEMPLATE = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"


def obter_vazamento_por_id(db: Session, vazamentoId: int):
    vazamento = db.query(models.Vazamento).filter(vazamentoId == models.Vazamento.id).first()
    if not vazamento:
        raise HTTPException(status_code=404, detail="Vazamento não encontrado")
    return vazamento


async def obter_vazamentos_pelo_email_usuario_e_salva_no_db(db: Session, email: str) -> list[schemas.VazamentoResponse]:
    """
    Obtém vazamentos de segurança associados a um e-mail.
    Busca localmente no banco ou externamente na API Have I Been Pwned.
    """
    usuario = UsuarioService.obter_usuario_pelo_email(db, email)
    vazamentos_locais = buscar_vazamentos_no_banco(db, usuario.id)
    if vazamentos_locais:
        return vazamentos_locais

    resultados_api = await buscar_vazamentos_na_api(email)

    if resultados_api:
        for vazamento_data in resultados_api:
            criar_vazamento_no_banco_de_dados(db, processar_vazamento(vazamento_data), usuario.id)

    return buscar_vazamentos_no_banco(db, usuario.id)


def buscar_vazamentos_no_banco(db: Session, usuario_id: int) -> list[schemas.VazamentoResponse]:
    """
    Busca vazamentos associados a um usuário no banco de dados.
    Garante que o campo data_classes seja retornado como uma lista válida.
    """
    vazamentos = db.query(models.Vazamento).filter(models.Vazamento.usuario_id == usuario_id).all()

    for vazamento in vazamentos:
        # Verifica se `data_classes` está armazenado como string e converte para lista
        if isinstance(vazamento.data_classes, str):
            try:
                vazamento.data_classes = json.loads(vazamento.data_classes)
            except json.JSONDecodeError:
                vazamento.data_classes = []  # Caso não seja um JSON válido, retorna lista vazia

    return vazamentos


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


def criar_vazamento_no_banco_de_dados(db: Session, vazamento_dados: dict, usuario_id: int):
    """
    Salva um vazamento no banco de dados associado a um usuário.
    """
    novo_vazamento = models.Vazamento(
        nome=vazamento_dados["nome"],
        titulo=vazamento_dados["titulo"],
        dominio_url=vazamento_dados["dominio_url"],
        data_vazamento=vazamento_dados["data_vazamento"],
        data_adicao=vazamento_dados["data_adicao"],
        data_atualizacao=vazamento_dados["data_atualizacao"],
        pwn_count=vazamento_dados["pwn_count"],
        descricao=vazamento_dados.get("descricao", ""),
        image_uri=vazamento_dados.get("image_uri", ""),
        usuario_id=usuario_id,
    )

    novo_vazamento.set_data_classes(vazamento_dados.get("data_classes", []))

    db.add(novo_vazamento)
    db.commit()
    db.refresh(novo_vazamento)
    return novo_vazamento


def get_all_vazamentos(db: Session, skip: int = 0, limit: int = 100):
    vazamentos = db.query(models.Vazamento).offset(skip).limit(limit).all()


    for vazamento in vazamentos:
        if isinstance(vazamento.data_classes, str):
            try:
                vazamento.data_classes = json.loads(vazamento.data_classes)
            except json.JSONDecodeError:
                vazamento.data_classes = []

    return vazamentos


async def notificar_vazamento_usuario_por_email_demonstrativo(email_usuario: str, titulo_vazamento: str, data: str, descricao: str, image_uri: str):
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


async def obter_vazamentos_pelo_email_usuario_e_salva_no_db_sem_verificacao_local(db: Session, email: str) -> list[schemas.VazamentoResponse]:
    """
    Obtém vazamentos de segurança associados a um e-mail, consultando a API,
    e só salva no banco de dados aqueles que são novos (não estão no banco),
    verificando os vazamentos pela combinação de 'Name' e 'BreachDate'. Retorna apenas
    vazamentos novos
    """

    usuario = UsuarioService.obter_usuario_pelo_email(db, email)

    resultados_api = await buscar_vazamentos_na_api(usuario.email)
    novos_vazamentos = []

    if resultados_api:
        for vazamento_data in resultados_api:

            vazamento_existente = buscar_vazamento_por_nome_e_data(db, vazamento_data['Name'], vazamento_data['BreachDate'], usuario.id)

            if not vazamento_existente:
                vazamento_salvo = criar_vazamento_no_banco_de_dados(db, processar_vazamento(vazamento_data), usuario.id)
                novos_vazamentos.append(vazamento_salvo)

    return novos_vazamentos


def buscar_vazamento_por_nome_e_data(db: Session, name: str, breach_date: str, usuario_id: int) -> schemas.VazamentoResponse:
    """
    Busca no banco de dados por um vazamento específico com o 'Name' e 'BreachDate' fornecidos e o id do usuário.
    Retorna o vazamento se encontrado, ou None se não existir.
    """
    return db.query(models.Vazamento).filter(
        models.Vazamento.nome == name,
        models.Vazamento.data_vazamento == breach_date,
        models.Vazamento.id == usuario_id
    ).first()

