import uuid

import bcrypt
from fastapi import HTTPException
from app.models.usuarios import UsuarioSchemas, UsuarioModel
from sqlalchemy.orm import Session
import logging


def obter_usuario_pelo_id(db: Session, usuarioId: uuid.UUID):
    logging.info(f"Tentando obter usuário pelo ID: {usuarioId}")
    usuario = db.query(UsuarioModel.Usuario).filter(usuarioId == UsuarioModel.Usuario.id).first()
    if not usuario:
        logging.warning(f"Usuário com ID {usuarioId} não encontrado.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    logging.info(f"Usuário com ID {usuarioId} encontrado.")
    return usuario


def obter_usuario_pelo_email(db: Session, user_email: str):
    logging.info(f"Tentando obter usuário pelo e-mail: {user_email}")
    usuario = db.query(UsuarioModel.Usuario).filter(user_email == UsuarioModel.Usuario.email).first()
    if not usuario:
        logging.warning(f"Usuário com e-mail {user_email} não encontrado.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    logging.info(f"Usuário com e-mail {user_email} encontrado.")
    return usuario


def criar_usuario(db: Session, usuario: UsuarioSchemas.CreateUserRequest):
    logging.info(f"Tentando criar usuário com e-mail: {usuario.email}")
    usuario_existente = db.query(UsuarioModel.Usuario).filter(usuario.email == UsuarioModel.Usuario.email).first()
    if usuario_existente:
        logging.warning(f"Já existe um usuário com o e-mail {usuario.email}.")
        raise ValueError("Já existe um usuário com esse e-mail.")

    senha_criptografada = bcrypt.hashpw(usuario.senha.encode('utf8'), bcrypt.gensalt())

    db_usuario = UsuarioModel.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=senha_criptografada.decode('utf-8')
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    logging.info(f"Usuário com e-mail {usuario.email} criado com sucesso.")
    return db_usuario


def atualizar_usuario(db: Session, usuario_id: uuid.UUID, usuario: UsuarioSchemas.UpdateUserRequest):
    logging.info(f"Tentando atualizar usuário com ID: {usuario_id}")
    usuariodb = obter_usuario_pelo_id(db, usuario_id)

    if usuario.email != usuariodb.email:
        logging.info(f"Alterando e-mail do usuário {usuariodb.email} para {usuario.email}")
        email_usuario_existente = db.query(UsuarioModel.Usuario).filter(
            usuario.email == UsuarioModel.Usuario.email).first()
        if email_usuario_existente:
            logging.warning(f"Já existe um usuário com o e-mail {usuario.email}.")
            raise ValueError("Já existe um usuário com esse e-mail.")

    if usuario.nome:
        logging.info(f"Alterando nome do usuário {usuariodb.nome} para {usuario.nome}")
        usuariodb.nome = usuario.nome
    if usuario.email:
        usuariodb.email = usuario.email
    if usuario.senha:
        senha_criptografada = bcrypt.hashpw(usuario.senha.encode('utf8'), bcrypt.gensalt())
        usuariodb.senha = senha_criptografada.decode('utf-8')
    if usuario.notificacoes_ativadas is not None:
        usuariodb.notificacoes_ativadas = usuario.notificacoes_ativadas

    db.commit()
    db.refresh(usuariodb)
    logging.info(f"Usuário com ID {usuario_id} atualizado com sucesso.")
    return usuariodb


def obter_lista_de_usuarios_com_notifacao_ativadas(db: Session):
    logging.info("Obtendo lista de usuários com notificações ativadas.")
    lista_de_usuarios_ativados = db.query(UsuarioModel.Usuario).filter(UsuarioModel.Usuario.notificacoes_ativadas == True).all()
    logging.info(f"{len(lista_de_usuarios_ativados)} usuários com notificações ativadas encontrados.")
    return lista_de_usuarios_ativados
