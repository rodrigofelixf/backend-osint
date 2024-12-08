import uuid
from operator import index

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base
from app.utils.assets.Images_url import usuario_avatar

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)  # UUID
    nome = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False, unique=True)
    senha = Column(String, index=True, nullable=False)
    avatar = Column(String, index=True, nullable=False, default=usuario_avatar)
    data_criacao = Column(DateTime, index=True, default=datetime.utcnow)
    role = Column(String, default="user", index=True)
    notificacoes_ativadas = Column(Boolean, index=True, default=False)

    vazamentos = relationship("Vazamento", back_populates="usuario")
