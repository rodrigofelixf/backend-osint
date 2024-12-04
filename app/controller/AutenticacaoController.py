from fastapi import APIRouter, Depends

from fastapi.security import OAuth2PasswordRequestForm
from pycparser.ply.yacc import token
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user
from app.services.AutenticacaoService import AutenticacaoService

routerautenticacao = APIRouter()



@routerautenticacao.get("/profile")
def read_user_profile(current_user: Usuario = Depends(get_current_user)):
    """Rota protegida que retorna o perfil do usuário"""
    return {"id": current_user.id, "email": current_user.email}


@routerautenticacao.post("/login")
def logar_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    autenticacao_service = AutenticacaoService(db)
    usuario_token = autenticacao_service.autenticar_usuario(email=form_data.username, password=form_data.password)
    return {"access_token": usuario_token, "token_type": "bearer"}