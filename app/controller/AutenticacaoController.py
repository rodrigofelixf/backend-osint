import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.autenticacao.login_schemas import LoginRequest, ErrorResponse
from app.models.usuarios.UsuarioModel import Usuario
from app.security.depends import get_current_user
from app.services.AutenticacaoService import AutenticacaoService

routerautenticacao = APIRouter()


@routerautenticacao.get(
    "/profile",
    summary="Obter dados do usuário logado",
    description="Endpoint protegido que retorna os dados do usuário atualmente autenticado, incluindo nome, e-mail e configurações.",
    responses={
        200: {
            "description": "Dados do usuário autenticado retornados com sucesso.",
        },
        401: {
            "description": "Token inválido ou ausente.",
            "model": ErrorResponse,
        },
    },
)
def obter_dados_do_usuario_logado(current_user: Usuario = Depends(get_current_user)):
    """
    **Obter o perfil do usuário autenticado.**

    - **current_user**: Usuário atualmente autenticado, obtido via token.

    **Respostas possíveis**:
    - **200 OK**: Retorna os dados do usuário autenticado.
    - **401 Unauthorized**: Token inválido ou ausente.

    **Exemplo de resposta**:
    ```json
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "nome": "João Silva",
        "email": "joao.silva@example.com",
        "avatar": "https://example.com/avatar.jpg",
        "notificacoes_ativadas": true
    }
    ```
    """
    logging.info(f"Usuário autenticado acessou o perfil: {current_user.email}")
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "notificacoes_ativadas": current_user.notificacoes_ativadas,
    }


@routerautenticacao.post(
    "/login",
    responses={
        401: {
            "description": "Credenciais inválidas ou autenticação falhou.",
            "model": ErrorResponse,
        },
        422: {
            "description": "Erro de validação do cliente. Dados enviados estão incorretos.",
            "model": ErrorResponse,
        },
        500: {
            "description": "Erro interno do servidor.",
            "model": ErrorResponse,
        },
    },
)
@routerautenticacao.post("/login")
def logar_usuario(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db_session)
):
    """
        **Autenticar um usuário.**

        Retorna um token de acesso se a autenticação for bem-sucedida.
        """
    logging.info(f"Tentativa de login para o e-mail: {form_data.username}")
    autenticacao_service = AutenticacaoService(db)
    try:
        usuario_token = autenticacao_service.autenticar_usuario(
            email=form_data.username, password=form_data.password
        )
        logging.info(f"Login bem-sucedido para o e-mail: {form_data.username}")
        return {"access_token": usuario_token, "token_type": "bearer"}
    except Exception as e:
        logging.warning(f"Falha no login para o e-mail {form_data.username}: {e}")
        raise HTTPException(status_code=401, detail=str(e))
