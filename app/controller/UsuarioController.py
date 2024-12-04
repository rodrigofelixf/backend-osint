import uuid

from fastapi import APIRouter, HTTPException, Depends, status

from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user

from app.models.usuarios import UsuarioModel, UsuarioSchemas
from app.db.database import SessionLocal, engine, get_db_session
from sqlalchemy.orm import Session
from typing import List

from app.services.UsuarioService import UsuarioService

routerusuarios = APIRouter()

endpointUsuario = "/usuarios/"



@routerusuarios.get(endpointUsuario + "{usuarioId}", response_model= UsuarioSchemas.UsuarioReponse)
def obter_usuario_por_id(usuarioId: uuid.UUID, db: Session= Depends(get_db_session)):
    usuario_service = UsuarioService(db)
    usuarioEncontrado = usuario_service.obter_usuario_pelo_id(usuarioId)
    return usuarioEncontrado

@routerusuarios.get(endpointUsuario + "procurar/{usuarioEmail}", response_model= UsuarioSchemas.UsuarioReponse)
def obter_usuario_por_email(usuarioEmail: str, db: Session= Depends(get_db_session), current_user: Usuario = Depends(get_current_user)):
    usuario_service = UsuarioService(db)
    usuarioEncontrado = usuario_service.obter_usuario_pelo_email(usuarioEmail)
    return usuarioEncontrado


@routerusuarios.post(endpointUsuario, response_model = UsuarioSchemas.UsuarioReponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioSchemas.CreateUserRequest, db: Session= Depends(get_db_session)):
    usuario_service = UsuarioService(db)
    usuario = usuario_service.criar_usuario(usuario)

    return  usuario

@routerusuarios.patch(endpointUsuario + "{usuario_id}", response_model = UsuarioSchemas.UsuarioReponse)
def atualizar_usuario(usuario_id: uuid.UUID, usuario: UsuarioSchemas.UpdateUserRequest, db: Session = Depends(get_db_session)):
    usuario_service = UsuarioService(db)
    try:
        usuario_atualizado = usuario_service.atualizar_usuario(usuario_id, usuario)
        return usuario_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))





