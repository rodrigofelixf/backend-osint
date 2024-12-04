from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.usuarios.UsuarioModel import Usuario
from app.security.security import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    email = payload.get("sub")
    usuario = db.query(Usuario).filter(email == Usuario.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
