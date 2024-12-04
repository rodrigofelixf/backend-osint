from fastapi import APIRouter, HTTPException, Depends

from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user
from app.services import VazamentoService
from app.models.vazamentos import models, schemas
from app.db.database import SessionLocal, engine, get_db_session
from sqlalchemy.orm import Session
from typing import List
from app.services.VazamentoService import notificar_vazamento_usuario_por_email_demonstrativo
import logging


# Configuração do roteador FastAPI
router = APIRouter()

endpointVazamento = "/vazamentos/"


@router.get(endpointVazamento + "procurar/{email}", response_model=List[schemas.VazamentoResponse])
async def obter_vazamentos_do_usuario_por_email(
        email: str,
        db: Session = Depends(get_db_session),
        current_user: Usuario = Depends(get_current_user)
):
    """Rota protegida para obter vazamentos de um usuário pelo email"""
    logging.info(f"Requisição recebida para buscar vazamentos do usuário com e-mail: {email}")


    if current_user.email != email:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar os vazamentos deste usuário.")

    try:
        vazamentoEncontrado = await VazamentoService.obter_vazamentos_pelo_email_usuario_e_salva_no_db(db, email)
        if vazamentoEncontrado:
            logging.info(f"Vazamentos encontrados para o e-mail: {email}")
        else:
            logging.warning(f"Nenhum vazamento encontrado para o e-mail: {email}")
        return vazamentoEncontrado
    except Exception as e:
        logging.error(f"Erro ao buscar vazamentos para o e-mail {email}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vazamentos")


@router.get(endpointVazamento + "exporvazamentos/", response_model=List[schemas.VazamentoResponse])
def expor_vazamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    logging.info(f"Requisição recebida para expor vazamentos com paginação (skip: {skip}, limit: {limit})")
    try:
        vazamentos = VazamentoService.get_all_vazamentos(db, skip, limit)
        if not vazamentos:
            logging.warning(f"Nenhum vazamento encontrado na paginação (skip: {skip}, limit: {limit})")
            raise HTTPException(status_code=404, detail="Nenhum vazamento encontrado")
        logging.info(f"{len(vazamentos)} vazamentos encontrados.")
        return vazamentos
    except Exception as e:
        logging.error(f"Erro ao expor vazamentos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao expor vazamentos")


@router.post(endpointVazamento + "notificar-vazamento-demonstrativo")
async def notificar_vazamento_demonstrativo(notificacao: schemas.NotificacaoRequest):
    logging.info(f"Requisição recebida para notificar sobre vazamento: {notificacao.titulo_vazamento}")
    try:
        await notificar_vazamento_usuario_por_email_demonstrativo(
            email_usuario=notificacao.email_usuario,
            titulo_vazamento=notificacao.titulo_vazamento,
            data=notificacao.data,
            descricao=notificacao.descricao,
            image_uri=notificacao.image_uri
        )
        logging.info(f"E-mail de notificação enviado com sucesso para {notificacao.email_usuario}.")
        return {"message": "E-mail enviado com sucesso!"}
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail para {notificacao.email_usuario}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail")
