import logging

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.usuarios.UsuarioModel import Usuario
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

        token = create_access_token(data={"sub": usuario.email})
        logging.info(f"Autenticação bem-sucedida para o e-mail: {email}")
        return token

    def obter_usuario_pelo_token(self, token: str):
        """Valida o token e retorna o usuário associado"""
        logging.info("Validação do token em andamento")

        payload = verify_access_token(token)
        email = payload.get("sub")
        if not email:
            logging.warning("Token inválido: campo 'sub' ausente")
            raise HTTPException(status_code=401, detail="Token inválido")

        usuario = self.db.query(Usuario).filter(email == Usuario.email).first()
        if not usuario:
            logging.warning(f"Usuário não encontrado para o e-mail: {email}")
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        logging.info(f"Usuário obtido pelo token: {email}")
        return usuario
