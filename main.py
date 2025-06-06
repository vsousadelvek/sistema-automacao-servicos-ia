import logging
from config import LOG_FILE_PATH, LOG_LEVEL, SCHEDULE_HOUR, SCHEDULE_MINUTE, SCHEDULE_SECOND
from scheduler.task_scheduler import schedule_task
from rpa_core.page_interactor import run_rpa_process
from utils.logger import setup_logging
from utils.security import get_credentials_securely

# Configura o sistema de logging
setup_logging(LOG_FILE_PATH, LOG_LEVEL)
logger = logging.getLogger(__name__)

def main():
    logger.info("Sistema SAMS iniciado.")

    # Obter credenciais de forma segura
    username, password = get_credentials_securely()
    if not username or not password:
        logger.error("Credenciais não fornecidas ou inválidas. O sistema não pode prosseguir.")
        return

    logger.info("Credenciais obtidas com sucesso.")

    # Agenda a tarefa principal da RPA
    logger.info(f"Agendando a tarefa RPA para iniciar às {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}:{SCHEDULE_SECOND:02d}...")
    schedule_task(
        task_function=run_rpa_process,
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        second=SCHEDULE_SECOND,
        username=username,
        password=password
    )

    logger.info("Agendador iniciado. Aguardando a execução da tarefa...")
    # O scheduler já está rodando em background, então o main.py pode finalizar aqui,
    # a menos que você queira mantê-lo rodando para alguma interação.
    # Para APScheduler, ele mantém o processo ativo.

if __name__ == "__main__":
    main()