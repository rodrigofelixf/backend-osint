import logging

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.db.redis.redis_cache import redis
from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user
from app.security.security import verify_password, create_access_token, verify_access_token


class AutenticacaoService:
    def __init__(self, db: Session):
        self.db = db

    def autenticar_usuario(self, email: str, password: str) -> str:
        """Autentica um usuário e retorna o token JWT"""
        logging.info(f"Tentativa de autenticação para o e-mail: {email}")

        usuario = self.db.query(Usuario).filter(email == Usuario.email).first()

        if not usuario or not verify_password(password, usuario.senha):
            logging.warning(f"Falha na autenticação para o e-mail: {email} - Credenciais inválidas")
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = create_access_token(data={"sub": usuario.email, "role": usuario.role})
        logging.info(f"Autenticação bem-sucedida para o e-mail: {email}")
        return token



def verify_role(role_necessaria: str):
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.role != role_necessaria:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer papel: {role_necessaria}"
            )
        return current_user

    return role_checker


def verify_roles(roles_permitidos: list):
    def roles_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer um dos papéis: {', '.join(roles_permitidos)}"
            )
        return current_user

    return roles_checker
