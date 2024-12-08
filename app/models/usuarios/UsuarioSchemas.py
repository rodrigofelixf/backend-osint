import uuid
from typing import Optional

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    nome: str
    email: str
    senha: str


class UsuarioReponse(BaseModel):
    id: uuid.UUID
    nome: str
    email: str
    avatar: str
    role: str
    notificacoes_ativadas: bool

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    role: Optional[str] = None
    notificacoes_ativadas: Optional[bool] = None




