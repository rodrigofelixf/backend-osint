import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.usuarios.UsuarioModel import Usuario
from app.models.vazamentos import schemas
from app.security.depends import get_current_user
from app.services.VazamentoService import VazamentoService

from app.utils.VazamentoUtils import notificar_vazamento_usuario_por_email_demonstrativo




# Configuração do roteador FastAPI
router = APIRouter()

endpointVazamento = "/vazamentos/"




@router.get(
    endpointVazamento + "procurar/{email}",
    response_model=List[schemas.VazamentoResponse],
    summary="Obter vazamentos pelo e-mail do usuário",
    description=(
        "Este endpoint protegido permite que um usuário autenticado obtenha "
        "os vazamentos associados ao e-mail informado. Apenas o próprio usuário pode acessar seus vazamentos."
    ),
    tags=["Vazamentos"]
)
async def obter_vazamentos_do_usuario_por_email(
    email: str,
    db: Session = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    **Obter vazamentos do usuário pelo e-mail.**

    - **email**: E-mail do usuário para buscar vazamentos.
    - **db**: Sessão de banco de dados injetada automaticamente.
    - **current_user**: Usuário atualmente autenticado.

    **Restrições**:
    - O usuário só pode acessar os vazamentos associados ao seu próprio e-mail.
    """
    logging.info(f"Requisição recebida para buscar vazamentos do usuário com e-mail: {email}")

    if current_user.email != email:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar os vazamentos deste usuário.")

    vazamento_service = VazamentoService(db)

    try:
        vazamentoEncontrado = await vazamento_service.obter_vazamentos_pelo_email_usuario_e_salva_no_db(email)
        if vazamentoEncontrado:
            logging.info(f"Vazamentos encontrados para o e-mail: {email}")
        else:
            logging.warning(f"Nenhum vazamento encontrado para o e-mail: {email}")
        return vazamentoEncontrado
    except Exception as e:
        logging.error(f"Erro ao buscar vazamentos para o e-mail {email}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar vazamentos")

"""@router.get(endpointVazamento + "exporvazamentos/", response_model=List[schemas.VazamentoResponse])
def expor_vazamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    logging.info(f"Requisição recebida para expor vazamentos com paginação (skip: {skip}, limit: {limit})")

    vazamento_service = VazamentoService(db)
    try:
        vazamentos = vazamento_service.get_all_vazamentos(skip, limit)
        if not vazamentos:
            logging.warning(f"Nenhum vazamento encontrado na paginação (skip: {skip}, limit: {limit})")
            raise HTTPException(status_code=404, detail="Nenhum vazamento encontrado")
        logging.info(f"{len(vazamentos)} vazamentos encontrados.")
        return vazamentos
    except Exception as e:
        logging.error(f"Erro ao expor vazamentos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao expor vazamentos") """


@router.post(
    endpointVazamento + "notificar-vazamento-demonstrativo",
    summary="Notificar sobre um vazamento (demonstrativo)",
    description=(
        "Este endpoint permite enviar notificações de vazamentos por e-mail, "
        "fornecendo os detalhes como título, descrição e imagem opcional."
    ),
    tags=["Vazamentos"],
    response_model=dict
)
async def notificar_vazamento_demonstrativo(notificacao: schemas.NotificacaoRequest):
    """
    **Enviar notificação sobre um vazamento (demonstrativo).**

    - **notificacao**: Dados necessários para enviar a notificação.
        - **email_usuario**: E-mail do destinatário.
        - **titulo_vazamento**: Título do vazamento.
        - **data**: Data do vazamento.
        - **descricao**: Descrição do vazamento.
        - **image_uri**: (Opcional) URL da imagem associada ao vazamento.

    **Retorna**:
    - Mensagem confirmando o envio ou um erro caso ocorra.
    """
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
        raise HTTPException(status_code=500, detail="Erro ao enviar e-mail")
