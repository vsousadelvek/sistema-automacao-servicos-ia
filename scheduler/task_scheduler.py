# sams_project/scheduler/task_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta, time
import logging

logger = logging.getLogger(__name__)

# O scheduler deve ser uma instância global ou gerenciada para não ser coletada pelo GC
scheduler = BackgroundScheduler()


def schedule_task(task_function, hour, minute, second, *args, **kwargs):
    """
    Agenda uma função para ser executada em uma data e hora específicas.
    A tarefa será agendada para a próxima ocorrência da data/hora.
    """
    # Calcula a próxima data e hora para a tarefa
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)

    # Se a hora alvo já passou hoje, agenda para o mesmo horário amanhã
    if target_time <= now:
        target_time += timedelta(days=1)
        logger.info(f"Horário agendado já passou hoje. Agendando para amanhã: {target_time}")
    else:
        logger.info(f"Agendando para hoje: {target_time}")

    # Adiciona a tarefa ao agendador
    scheduler.add_job(
        task_function,
        trigger=DateTrigger(run_date=target_time),
        args=args,
        kwargs=kwargs,
        id="rpa_service_booking_task"
    )

    # Inicia o scheduler se ainda não estiver rodando
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler iniciado em background.")
    else:
        logger.info("APScheduler já está rodando. Tarefa adicionada.")

    logger.info(f"Tarefa '{task_function.__name__}' agendada para: {target_time}")


# Exemplo de uso:
if __name__ == '__main__':
    from utils.logger import setup_logging

    setup_logging("scheduler_test.log", "INFO")


    def test_task(msg):
        logger.info(f"Executando tarefa de teste: {msg} em {datetime.now()}")


    # Agenda a tarefa de teste para daqui a 10 segundos
    future_time = datetime.now() + timedelta(seconds=10)
    schedule_task(test_task, future_time.hour, future_time.minute, future_time.second, msg="Olá do agendador!")

    logger.info("Aguardando a tarefa de teste...")
    try:
        # Mantém o processo principal rodando para que o scheduler possa executar a tarefa
        # Em um ambiente real, o main.py manterá isso.
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler desligado.")