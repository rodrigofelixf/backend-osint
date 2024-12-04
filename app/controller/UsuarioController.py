import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.testing.plugin.plugin_base import logging

from app.db.database import get_db_session
from app.models.usuarios import UsuarioSchemas
from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user
from app.services.UsuarioService import UsuarioService

routerusuarios = APIRouter()


endpointUsuario = "/usuarios/"
@routerusuarios.get(
    endpointUsuario + "{usuarioId}",
    response_model=UsuarioSchemas.UsuarioReponse,
    summary="Obter usuário por ID",
    description=(
        "Este endpoint permite buscar um usuário pelo seu ID. "
        "O ID deve ser um UUID válido."
    ),
    tags=["Usuários"]
)
def obter_usuario_por_id(usuarioId: uuid.UUID, db: Session = Depends(get_db_session)):
    logging.info(f"Recebida solicitação para obter usuário com ID: {usuarioId}")
    usuario_service = UsuarioService(db)
    usuarioEncontrado = usuario_service.obter_usuario_pelo_id(usuarioId)
    if not usuarioEncontrado:
        logging.warning(f"Usuário com ID {usuarioId} não encontrado.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    logging.info(f"Usuário com ID {usuarioId} encontrado com sucesso.")
    return usuarioEncontrado

@routerusuarios.get(
    endpointUsuario + "procurar/{usuarioEmail}",
    response_model=UsuarioSchemas.UsuarioReponse,
    summary="Obter usuário por e-mail",
    description=(
        "Este endpoint permite buscar um usuário pelo e-mail. "
        "O e-mail informado deve estar registrado no sistema."
    ),
    tags=["Usuários"]
)
def obter_usuario_por_email(
    usuarioEmail: str,
    db: Session = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    logging.info(f"Recebida solicitação para obter usuário com e-mail: {usuarioEmail}")
    usuario_service = UsuarioService(db)
    usuarioEncontrado = usuario_service.obter_usuario_pelo_email(usuarioEmail)
    if not usuarioEncontrado:
        logging.warning(f"Usuário com e-mail {usuarioEmail} não encontrado.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    logging.info(f"Usuário com e-mail {usuarioEmail} encontrado com sucesso.")
    return usuarioEncontrado

@routerusuarios.post(
    endpointUsuario,
    response_model=UsuarioSchemas.UsuarioReponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo usuário",
    description=(
        "Este endpoint permite criar um novo usuário no sistema. "
        "Os dados obrigatórios incluem nome, e-mail e senha."
    ),
    tags=["Usuários"]
)
def criar_usuario(usuario: UsuarioSchemas.CreateUserRequest, db: Session = Depends(get_db_session)):
    logging.info("Recebida solicitação para criar um novo usuário.")
    usuario_service = UsuarioService(db)
    try:
        usuario = usuario_service.criar_usuario(usuario)
        logging.info(f"Usuário criado com sucesso: {usuario.email}")
        return usuario
    except ValueError as e:
        logging.error(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@routerusuarios.patch(
    endpointUsuario + "/admin/{usuario_id}",
    response_model=UsuarioSchemas.UsuarioReponse,
    summary="Atualizar dados de um usuário",
    description=(
        "Este endpoint permite que um administrador atualize os dados de um usuário existente. "
        "Os dados podem incluir nome, e-mail, senha e notificacoes ativadas."
    ),
    tags=["Usuários"]
)
def atualizar_usuario(
    usuario_id: uuid.UUID,
    usuario: UsuarioSchemas.UpdateUserRequest,
    db: Session = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    logging.info(f"Recebida solicitação para atualizar o usuário com ID: {usuario_id}")
    usuario_service = UsuarioService(db)
    try:
        usuario_atualizado = usuario_service.atualizar_usuario(usuario_id, usuario)
        logging.info(f"Usuário com ID {usuario_id} atualizado com sucesso.")
        return usuario_atualizado
    except ValueError as e:
        logging.error(f"Erro de validação ao atualizar usuário com ID {usuario_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erro ao atualizar usuário com ID {usuario_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")