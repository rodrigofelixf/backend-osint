from datetime import datetime
from fastapi import FastAPI


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from starlette.middleware.cors import CORSMiddleware

from app.controller.VazamentoController import router as api_router
from app.controller.UsuarioController import routerusuarios as api_router_usuarios
from app.controller.AutenticacaoController import routerautenticacao as api_router_autenticacao
from app.db.database import Base, engine
from app.services.automacoes.TarefaVazamento import iniciar_agendador

import logging
import os

LOG_FILE_PATH = os.path.join(os.getcwd(), "aplicacao-logs.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOG_FILE_PATH,
    filemode="a"
)

logging.info("Configuração de log iniciada.")

logging.info("Teste: configurando o logging.")

app = FastAPI()

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:5173",
    ["*"]# Coloque as origens corretas
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite todas as origens; ajuste conforme necessário
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos; ajuste conforme necessário
    allow_headers=["*"],  # Permite todos os cabeçalhos; ajuste conforme necessário
)

app.include_router(api_router, prefix="/v1/api", tags=["Vazamentos"])
app.include_router(api_router_usuarios, prefix="/v1/api")
app.include_router(api_router_autenticacao, prefix="/v1/api", tags=["Autenticacao"])

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    global scheduler
    scheduler = iniciar_agendador()
    logging.info("Agendador iniciado junto com a API.")  # Usando logs


@app.on_event("shutdown")
async def shutdown_event():
    if scheduler:
        scheduler.shutdown()
        logging.info("Agendador encerrado com a API.")  # Usando logs


@app.get("/")
async def root():
    logging.info("Rota principal '/' acessada.")  # Log de acesso à rota principal
    return {"message": "API está rodando com agendador integrado!"}


@app.get("/hora_atual")
async def hora_atual():
    return {"hora_atual": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}