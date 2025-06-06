# sams_project/models/captcha_solver/dataset_creator.py

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from config import DRIVER_PATH, SITE_URL, HEADLESS_MODE
import logging

from utils.logger import setup_logging

setup_logging("dataset_creator_log.log", "INFO")
logger = logging.getLogger(__name__)

def create_initial_dataset_files():
    """Cria os arquivos e pastas iniciais se não existirem."""
    captcha_images_dir = os.path.join(os.path.dirname(__file__), 'data', 'captcha_images')
    labels_file = os.path.join(os.path.dirname(__file__), 'data', 'labels.csv')

    os.makedirs(captcha_images_dir, exist_ok=True)
    if not os.path.exists(labels_file):
        df = pd.DataFrame(columns=['image_name', 'label'])
        df.to_csv(labels_file, index=False)
        logger.info(f"Arquivo de rótulos criado em: {labels_file}")
    else:
        logger.info(f"Arquivo de rótulos já existe em: {labels_file}")
    logger.info(f"Pasta de imagens CAPTCHA: {captcha_images_dir}")

def collect_and_label_captcha():
    """
    Coleta imagens de CAPTCHA do site e permite rotulagem manual.
    Este é um script semi-automático que exige interação manual.
    """
    create_initial_dataset_files()

    captcha_images_dir = os.path.join(os.path.dirname(__file__), 'data', 'captcha_images')
    labels_file = os.path.join(os.path.dirname(__file__), 'data', 'labels.csv')

    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Tenta usar o driver manager, senão usa o caminho manual
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("ChromeDriver iniciado via WebDriverManager.")
    except Exception as e:
        logger.warning(f"WebDriverManager falhou ({e}). Tentando usar DRIVER_PATH configurado.")
        try:
            service = ChromeService(executable_path=DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
            logger.info(f"ChromeDriver iniciado usando DRIVER_PATH: {DRIVER_PATH}.")
        except Exception as e_manual:
            logger.error(f"Não foi possível iniciar o ChromeDriver: {e_manual}. Certifique-se de que o driver está em '{DRIVER_PATH}' e é compatível.")
            return

    try:
        driver.get(SITE_URL)
        logger.info(f"Navegando para: {SITE_URL}")
        time.sleep(3) # Tempo para a página carregar

        while True:
            try:
                # Altere este seletor para o seletor CSS/XPath real da imagem do CAPTCHA no site!
                # Exemplo: Se o CAPTCHA é uma imagem com ID "captcha_img"
                captcha_img_element = driver.find_element(By.ID, "captcha_img")
                # Ou By.CSS_SELECTOR, By.XPATH, etc.
                # captcha_img_element = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]")

                # Salvar a imagem do CAPTCHA
                timestamp = int(time.time())
                image_name = f"captcha_{timestamp}.png"
                image_path = os.path.join(captcha_images_dir, image_name)
                captcha_img_element.screenshot(image_path)
                logger.info(f"CAPTCHA capturado: {image_name}. Por favor, rotule-o.")

                # Solicitar rotulagem manual
                label = input(f"Digite o texto do CAPTCHA para '{image_name}' (ou 'q' para sair, 'r' para recarregar): ").strip().upper()

                if label == 'Q':
                    break
                elif label == 'R':
                    driver.refresh()
                    logger.info("Página recarregada para novo CAPTCHA.")
                    time.sleep(2) # Tempo para recarregar
                    continue
                else:
                    # Adicionar ao CSV
                    df = pd.read_csv(labels_file)
                    new_row = pd.DataFrame([{'image_name': image_name, 'label': label}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(labels_file, index=False)
                    logger.info(f"CAPTCHA '{image_name}' rotulado como '{label}'. Total de amostras: {len(df)}")
                    # Recarregue a página para obter um novo CAPTCHA
                    driver.refresh()
                    time.sleep(2) # Tempo para recarregar

            except Exception as e:
                logger.error(f"Erro ao capturar ou rotular CAPTCHA: {e}")
                logger.info("Tentando recarregar a página para continuar a coleta...")
                driver.refresh()
                time.sleep(5) # Espera um pouco mais após erro

    except KeyboardInterrupt:
        logger.info("Coleta de CAPTCHA interrompida pelo usuário.")
    finally:
        driver.quit()
        logger.info("Navegador fechado.")

if __name__ == "__main__":
    create_initial_dataset_files() # Garante que as pastas/arquivos existam
    print("\n--- INICIANDO COLETOR E ROTULADOR DE CAPTCHA ---")
    print("Este script abrirá o navegador. Você precisará digitar o CAPTCHA no console.")
    print("Digite 'q' para sair ou 'r' para recarregar a página e obter um novo CAPTCHA.")
    input("Pressione Enter para iniciar...")
    collect_and_label_captcha()
    print("Coleta de CAPTCHA finalizada.")
    print("Lembre-se de treinar seu modelo de IA após coletar dados suficientes!")