# sams_project/rpa_core/browser_manager.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from config import DRIVER_PATH, BROWSER_TYPE, HEADLESS_MODE
import logging

logger = logging.getLogger(__name__)

def get_browser_options():
    """Configura as opções do navegador (headless, User-Agent, etc.)."""
    if BROWSER_TYPE == "chrome":
        options = webdriver.ChromeOptions()
        # Argumentos básicos para otimização e estabilidade
        options.add_argument("--no-sandbox") # Essencial para Linux, bom para segurança
        options.add_argument("--disable-dev-shm-usage") # Para ambientes Docker/Linux
        options.add_argument("--disable-blink-features=AutomationControlled") # Esconde algumas detecções
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if HEADLESS_MODE:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu") # Necessário para headless no Windows
            options.add_argument("--window-size=1920,1080") # Define um tamanho de janela para headless

        # Configurar User-Agent (ex: para parecer um Chrome real)
        # É uma boa prática buscar um User-Agent atualizado
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        # options.add_argument(f"user-agent={user_agent}")

        return options
    elif BROWSER_TYPE == "firefox":
        options = webdriver.FirefoxOptions()
        if HEADLESS_MODE:
            options.add_argument("--headless")
        # Adicione outras opções específicas do Firefox se necessário
        return options
    else:
        raise ValueError("Tipo de navegador não suportado em config.py")

def init_driver():
    """Inicializa e retorna uma instância do WebDriver."""
    options = get_browser_options()
    driver = None
    service = None

    try:
        if BROWSER_TYPE == "chrome":
            # Tenta usar WebDriverManager
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("ChromeDriver iniciado via WebDriverManager.")
        elif BROWSER_TYPE == "firefox":
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            logger.info("GeckoDriver iniciado via WebDriverManager.")

    except Exception as e:
        logger.warning(f"WebDriverManager falhou para {BROWSER_TYPE} ({e}). Tentando usar DRIVER_PATH configurado.")
        try:
            if BROWSER_TYPE == "chrome":
                service = ChromeService(executable_path=DRIVER_PATH)
                driver = webdriver.Chrome(service=service, options=options)
            elif BROWSER_TYPE == "firefox":
                service = FirefoxService(executable_path=DRIVER_PATH)
                driver = webdriver.Firefox(service=service, options=options)
            logger.info(f"Driver {BROWSER_TYPE} iniciado usando DRIVER_PATH: {DRIVER_PATH}.")
        except Exception as e_manual:
            logger.error(f"Não foi possível iniciar o WebDriver: {e_manual}. Verifique 'config.py' e o driver.")
            return None

    if driver:
        # Script para evitar detecção de WebDriver (executado após abrir a página)
        # Isso tenta ocultar a propriedade 'navigator.webdriver'
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        logger.info("Executado script para ocultar 'navigator.webdriver'.")

    return driver

def quit_driver(driver):
    """Fecha o WebDriver."""
    if driver:
        driver.quit()
        logger.info("Navegador fechado.")