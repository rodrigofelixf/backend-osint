from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.usuarios.UsuarioModel import Usuario
from app.security.security import verify_password, create_access_token, verify_access_token


class AutenticacaoService:
    def __init__(self, db: Session):
        self.db = db



    def autenticar_usuario(self, email: str, password: str) -> str:
        """Autentica um usuário e retorna o token JWT"""
        usuario = self.db.query(Usuario).filter(email == Usuario.email).first()
        if not usuario or not verify_password(password, usuario.senha):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = create_access_token(data={"sub": usuario.email})
        return token

    def obter_usuario_pelo_token(self, token: str):
        """Valida o token e retorna o usuário associado"""
        payload = verify_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")

        usuario = self.db.query(Usuario).filter(email == Usuario.email).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return usuario
