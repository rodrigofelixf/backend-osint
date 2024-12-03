import uuid

from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class VazamentoBase(BaseModel):
    nome: str
    titulo: str
    dominio_url: str
    data_vazamento: Optional[date]
    data_atualizacao: Optional[datetime]
    descricao: Optional[str] = None
    image_uri: Optional[str] = None

class VazamentoCreate(BaseModel):
    nome: str
    titulo: str
    dominio_url: str
    data_vazamento: Optional[date]
    data_atualizacao: Optional[datetime]
    descricao: Optional[str] = None
    image_uri: Optional[str] = None
    usuario_id: uuid.UUID


class VazamentoResponse(BaseModel):
    id: int
    nome: str
    titulo: str
    dominio_url: str
    data_vazamento: Optional[date]
    data_adicao: Optional[datetime]
    data_atualizacao: Optional[datetime]
    pwn_count: int
    descricao: Optional[str] = None
    image_uri: Optional[str] = None
    data_classes: List[str] = []  # Lista de strings
    usuario_id: uuid.UUID

    class Config:
        from_attributes = True


class NotificacaoRequest(BaseModel):
    email_usuario: str
    titulo_vazamento: str
    data: str
    descricao: str
    image_uri: str