from datetime import datetime
import logging
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.controller.AutenticacaoController import routerautenticacao as api_router_autenticacao
from app.controller.UsuarioController import routerusuarios as api_router_usuarios
from app.controller.VazamentoController import router as api_router
from app.db.database import Base, engine
from app.db.redis.redis_cache import redis
from app.services.automacoes.TarefaVazamento import iniciar_agendador

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

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1/api", tags=["Vazamentos"])
app.include_router(api_router_usuarios, prefix="/v1/api")
app.include_router(api_router_autenticacao, prefix="/v1/api", tags=["Autenticacao"])

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    global scheduler
    scheduler = iniciar_agendador()
    logging.info("Agendador iniciado junto com a API.")


@app.on_event("shutdown")
async def shutdown_event():
    if scheduler:
        scheduler.shutdown()
        logging.info("Agendador encerrado com a API.")

    await redis.close()
    logging.info("Conexão com o Redis encerrada.")



@app.get("/")
async def root():
    logging.info("Rota principal '/' acessada.")
    return {"message": "API está rodando com agendador integrado!"}


@app.get("/hora_atual")
async def hora_atual():
    return {"hora_atual": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}




