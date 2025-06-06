# sams_project/utils/logger.py

import logging
import os

def setup_logging(log_file_path, level_str="INFO"):
    """
    Configura o sistema de logging para o projeto.
    Mensagens serão enviadas para o console e para um arquivo.
    """
    # Mapear strings de nível para objetos de nível de logging
    level = getattr(logging, level_str.upper(), logging.INFO)

    # Criar o diretório de logs se não existir
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler() # Para exibir no console
        ]
    )
    # Define o nível de log para bibliotecas barulhentas
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO) # Mantenha INFO para mensagens do APScheduler
    logging.getLogger('PIL').setLevel(logging.WARNING) # Pillow (PIL)
    logging.getLogger('torch').setLevel(logging.WARNING) # PyTorch

    logging.info(f"Logging configurado. Nível: {level_str}. Log file: {log_file_path}")

# Exemplo de uso (para teste, não será executado diretamente no fluxo principal)
if __name__ == '__main__':
    setup_logging("test_log.log", "DEBUG")
    logger = logging.getLogger(__name__)
    logger.debug("Mensagem de debug de teste.")
    logger.info("Mensagem de informação de teste.")
    logger.warning("Mensagem de aviso de teste.")
    logger.error("Mensagem de erro de teste.")
    try:
        raise ValueError("Exemplo de erro")
    except ValueError:
        logger.exception("Exceção capturada com logger.exception.")