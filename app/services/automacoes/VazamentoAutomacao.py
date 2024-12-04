import logging
from app.db.database import SessionLocal, get_db_session
from app.services import EmailService
from app.services.UsuarioService import UsuarioService
from app.services.VazamentoService import VazamentoService


def gerar_mensagem_html_multi(usuario_nome: str, vazamentos: list):
    vazamentos_html = "".join([
        f"""
        <div class="vazamento-item">
            <h3>{vazamento['titulo']}</h3>
            <p><strong>Data:</strong> {vazamento['data']}</p>
            <p><strong>Descrição:</strong> {vazamento['descricao']}</p>
            <div class="image-container">
                <img src="{vazamento['image_uri']}" alt="Imagem do Vazamento">
            </div>
        </div>
        """
        for vazamento in vazamentos
    ])

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notificação de Vazamentos</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; }}
            .header {{ background-color: #4CAF50; color: white; text-align: center; padding: 10px; }}
            .vazamento-item {{ border-bottom: 1px solid #ddd; padding: 15px 0; }}
            .vazamento-item img {{ max-width: 100%; border-radius: 8px; }}
            .footer {{ text-align: center; color: #888888; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Notificação de Vazamentos</h2>
            </div>
            <p>Olá {usuario_nome},</p>
            <p>Identificamos os seguintes vazamentos relacionados ao seu e-mail:</p>
            {vazamentos_html}
            <div class="footer">
                <p>Atenciosamente,</p>
                <p><strong>Equipe de Segurança Start Osinc Sec - SOS</strong></p>
            </div>
        </div>
    </body>
    </html>
    """


async def automatizar_notificacao_vazamentos():
    logging.info("Iniciando a tarefa de notificação de vazamentos.")
    try:
        db = next(get_db_session())
        usuario_service = UsuarioService(db)
        usuarios_com_notificacoes = usuario_service.obter_lista_de_usuarios_com_notifacao_ativadas()
        if not usuarios_com_notificacoes:
            logging.info("Nenhum usuário com notificações ativas foi encontrado.")
            return

        vazamento_service = VazamentoService(db)
        for usuario in usuarios_com_notificacoes:
            vazamentos = await vazamento_service.obter_vazamentos_pelo_email_usuario_e_salva_no_db_sem_verificacao_local(
                usuario.email
            )

            if vazamentos:
                vazamentos_formatados = [
                    {
                        "titulo": vazamento.titulo,
                        "data": vazamento.data_vazamento.strftime('%d/%m/%Y'),
                        "descricao": vazamento.descricao,
                        "image_uri": vazamento.image_uri
                    }
                    for vazamento in vazamentos
                ]

                mensagem_html = gerar_mensagem_html_multi(usuario.nome, vazamentos_formatados)
                assunto = f"Notificação de Vazamentos: {len(vazamentos)} novos"
                await EmailService.enviar_email(usuario.email, assunto, mensagem_html)
                logging.info(f"E-mail enviado para {usuario.email} com {len(vazamentos)} vazamentos.")
            else:
                logging.info(f"Nenhum novo vazamento encontrado para o usuário: {usuario.email}")

    except Exception as e:
        logging.error(f"Erro durante a execução da automação: {e}")
