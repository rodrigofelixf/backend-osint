import uuid
from typing import Optional
import httpx
import os
from fastapi import HTTPException
from datetime import datetime
from dotenv import load_dotenv
from app.models.vazamentos import models, schemas
from sqlalchemy.orm import Session

from app.services.EmailService import enviar_email
import json

from app.services.UsuarioService import UsuarioService
from app.utils.VazamentoUtils import buscar_vazamentos_na_api, processar_vazamento


class VazamentoService:
    def __init__(self, db: Session):
        self.db = db



    def obter_vazamento_por_id(self, vazamentoId: int):
        vazamento = self.db.query(models.Vazamento).filter(vazamentoId == models.Vazamento.id).first()
        if not vazamento:
            raise HTTPException(status_code=404, detail="Vazamento não encontrado")
        return vazamento


    async def obter_vazamentos_pelo_email_usuario_e_salva_no_db(self, email: str) -> list[schemas.VazamentoResponse]:
        """
        Obtém vazamentos de segurança associados a um e-mail.
        Busca localmente no banco ou externamente na API Have I Been Pwned.
        """
        usuario_service = UsuarioService(self.db)
        usuario = usuario_service.obter_usuario_pelo_email(email)
        vazamentos_locais = self.buscar_vazamentos_no_banco(usuario.id)
        if vazamentos_locais:
            return vazamentos_locais

        resultados_api = await buscar_vazamentos_na_api(email)

        if resultados_api:
            for vazamento_data in resultados_api:
                self.criar_vazamento_no_banco_de_dados(processar_vazamento(vazamento_data), usuario.id)

        return self.buscar_vazamentos_no_banco(usuario.id)


    def buscar_vazamentos_no_banco(self, usuario_id: uuid.UUID) -> list[models]:
        """
        Busca vazamentos associados a um usuário no banco de dados.
        Garante que o campo data_classes seja retornado como uma lista válida.
        """
        vazamentos = self.db.query(models.Vazamento).filter(usuario_id == models.Vazamento.usuario_id).all()

        for vazamento in vazamentos:
            # Verifica se `data_classes` está armazenado como string e converte para lista
            if isinstance(vazamento.data_classes, str):
                try:
                    vazamento.data_classes = json.loads(vazamento.data_classes)
                except json.JSONDecodeError:
                    vazamento.data_classes = []  # Caso não seja um JSON válido, retorna lista vazia

        return vazamentos


    def criar_vazamento_no_banco_de_dados(self, vazamento_dados: dict, usuario_id: uuid.UUID):
        """
        Salva um vazamento no banco de dados associado a um usuário.
        """
        novo_vazamento = models.Vazamento(
            nome=vazamento_dados["nome"],
            titulo=vazamento_dados["titulo"],
            dominio_url=vazamento_dados["dominio_url"],
            data_vazamento=vazamento_dados["data_vazamento"],
            data_adicao=vazamento_dados["data_adicao"],
            data_atualizacao=vazamento_dados["data_atualizacao"],
            pwn_count=vazamento_dados["pwn_count"],
            descricao=vazamento_dados.get("descricao", ""),
            image_uri=vazamento_dados.get("image_uri", ""),
            usuario_id=usuario_id,
        )

        novo_vazamento.set_data_classes(vazamento_dados.get("data_classes", []))

        self.db.add(novo_vazamento)
        self.db.commit()
        self.db.refresh(novo_vazamento)
        return novo_vazamento


    def get_all_vazamentos(self, skip: int = 0, limit: int = 100):
        vazamentos = self.db.query(models.Vazamento).offset(skip).limit(limit).all()


        for vazamento in vazamentos:
            if isinstance(vazamento.data_classes, str):
                try:
                    vazamento.data_classes = json.loads(vazamento.data_classes)
                except json.JSONDecodeError:
                    vazamento.data_classes = []

        return vazamentos


    async def obter_vazamentos_pelo_email_usuario_e_salva_no_db_sem_verificacao_local(self, email: str) -> list[schemas.VazamentoResponse]:
        """
        Obtém vazamentos de segurança associados a um e-mail, consultando a API,
        e só salva no banco de dados aqueles que são novos (não estão no banco),
        verificando os vazamentos pela combinação de 'Name' e 'BreachDate'. Retorna apenas
        vazamentos novos
        """

        usuario_service = UsuarioService(self.db)
        usuario = usuario_service.obter_usuario_pelo_email(email)

        resultados_api = await buscar_vazamentos_na_api(usuario.email)
        novos_vazamentos = []

        if resultados_api:
            for vazamento_data in resultados_api:

                vazamento_existente = self.buscar_vazamento_por_nome_e_data(vazamento_data['Name'], vazamento_data['BreachDate'], usuario.id)

                if not vazamento_existente:
                    vazamento_salvo = self.criar_vazamento_no_banco_de_dados(processar_vazamento(vazamento_data), usuario.id)
                    novos_vazamentos.append(vazamento_salvo)

        return novos_vazamentos


    def buscar_vazamento_por_nome_e_data(self, name: str, breach_date: str, usuario_id: uuid.UUID) -> models:
        """
        Busca no banco de dados por um vazamento específico com o 'Name' e 'BreachDate' fornecidos e o id do usuário.
        Retorna o vazamento se encontrado, ou None se não existir.
        """
        return self.db.query(models.Vazamento).filter(
            name == models.Vazamento.nome,
            breach_date == models.Vazamento.data_vazamento,
            usuario_id == models.Vazamento.usuario_id
        ).first()

