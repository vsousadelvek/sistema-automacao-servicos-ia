# sams_project/config.py

import os

# Configurações do Site Alvo
SITE_URL = "https://www.proeis.rj.gov.br/Default.aspx"  # Substitua pelo URL real do site da Priscila

# Configurações do Navegador
BROWSER_TYPE = "chrome"  # Ou "firefox"
HEADLESS_MODE = True     # Rodar o navegador em modo oculto (True para produção, False para depuração)

# Caminho para o Driver do Navegador
# Certifique-se de que o driver (ex: chromedriver.exe) está na pasta 'drivers/'
# E que a versão do driver é compatível com a versão do seu navegador.
DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver.exe') # Para Windows
# DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver') # Para Linux/macOS

# Caminhos para Modelos e Dados de IA
CAPTCHA_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'captcha_solver', 'trained_model.pth')
CAPTCHA_DATA_DIR = os.path.join(os.path.dirname(__file__), 'models', 'data', 'captcha_images')
CAPTCHA_LABELS_FILE = os.path.join(os.path.dirname(__file__), 'models', 'data', 'labels.csv')

# Configurações de Log
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'sams_log.log')
LOG_LEVEL = "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Configurações do Agendador (APScheduler)
SCHEDULE_HOUR = 6      # Hora de início (0-23)
SCHEDULE_MINUTE = 0    # Minuto de início (0-59) - Ajustado para iniciar 10 segundos antes das 6h
SCHEDULE_SECOND = 0    # Segundo de início (0-59)

# Tempo limite para operações do Selenium (em segundos)
SELENIUM_TIMEOUT = 30

# ---- ATENÇÃO: NÃO COLOQUE CREDENCIAIS DIRETAMENTE AQUI ----
# Use variáveis de ambiente, ou um métodoseguro de input/armazenamento.
# Exemplo de como acessar uma variável de ambiente:
USERNAME = os.getenv("")
PASSWORD = os.getenv("")