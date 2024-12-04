import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.automacoes.VazamentoAutomacao import automatizar_notificacao_vazamentos


def iniciar_agendador():
    brt = pytz.timezone("America/Sao_Paulo")
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(day_of_week="sun", hour=20, minute=00, timezone=brt)
    scheduler.add_job(automatizar_notificacao_vazamentos, trigger)
    scheduler.start()
    logging.info("Agendador iniciado. Próxima execução programada para domingo às 20:00.")
    return scheduler
