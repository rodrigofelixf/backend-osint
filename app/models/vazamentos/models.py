import json
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Vazamento(Base):
    __tablename__ = "vazamentos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    titulo = Column(String, index=True)
    dominio_url = Column(String, index=True)
    data_vazamento = Column(Date, nullable=True)
    data_adicao = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, nullable=True)
    pwn_count = Column(Integer, nullable=True)
    descricao = Column(Text, nullable=True)
    image_uri = Column(String, nullable=True)
    data_classes = Column(Text, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="vazamentos")


    def get_data_classes(self):
        return json.loads(self.data_classes) if self.data_classes else []

    def set_data_classes(self, data_classes_list):
        self.data_classes = json.dumps(data_classes_list)

