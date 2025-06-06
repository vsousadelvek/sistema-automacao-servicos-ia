# sams_project/rpa_core/page_interactor.py

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import os

from config import SITE_URL, SELENIUM_TIMEOUT, CAPTCHA_MODEL_PATH, \
    CAPTCHA_DATA_DIR  # Inclua DATA_DIR para inferir chars
from rpa_core.browser_manager import init_driver, quit_driver
from rpa_core.anti_detection import apply_human_like_delays
from models.captcha_solver.predict import load_captcha_model, solve_captcha
from models.captcha_solver.train import CaptchaDataset  # Para metadados do CAPTCHA dataset
from PIL import Image

logger = logging.getLogger(__name__)


def run_rpa_process(username, password):
    """
    Função principal que executa o processo de automação.
    """
    logger.info("Iniciando processo RPA para marcação de serviços...")
    driver = None
    captcha_model = None
    device = None

    try:
        # --- 1. Carregar Modelo de CAPTCHA ---
        # Estes parâmetros devem corresponder aos usados no treinamento do seu modelo.
        # Precisamos de uma forma para inferir o num_captcha_characters e num_classes_per_char
        # antes de carregar o modelo, se o labels.csv não tiver sido lido.
        # Uma forma é passar esses valores como parâmetros em config.py
        # ou inferir a partir do dataset_creator/labels.csv
        try:
            # Carrega um dataset dummy apenas para obter os metadados de caracteres
            # Assume que labels.csv já existe e tem pelo menos uma linha de dados
            dummy_dataset = CaptchaDataset(CAPTCHA_DATA_DIR, os.path.join(CAPTCHA_DATA_DIR, '..', 'labels.csv'))
            NUM_CAPTCHA_CHARACTERS = len(dummy_dataset.labels_df.iloc[0, 1])
            NUM_CLASSES_PER_CHAR = dummy_dataset.num_classes_per_char

            captcha_model, device = load_captcha_model(
                num_captcha_characters=NUM_CAPTCHA_CHARACTERS,
                num_classes_per_char=NUM_CLASSES_PER_CHAR,
                img_height=60,  # Ajuste para o tamanho real do seu CAPTCHA
                img_width=120  # Ajuste para o tamanho real do seu CAPTCHA
            )
            if captcha_model is None:
                logger.error("Falha ao carregar o modelo de CAPTCHA. Abortando RPA.")
                return False
        except Exception as e:
            logger.error(f"Erro ao inferir parâmetros do modelo de CAPTCHA ou carregar dataset: {e}. Abortando RPA.")
            logger.error("Certifique-se de que 'models/data/labels.csv' está populado com pelo menos uma amostra.")
            return False

        # --- 2. Inicializar o Navegador ---
        driver = init_driver()
        if not driver:
            logger.error("Não foi possível inicializar o navegador. Abortando RPA.")
            return False

        driver.get(SITE_URL)
        logger.info(f"Navegado para o site: {SITE_URL}")
        apply_human_like_delays()

        # --- 3. Executar o Login ---
        logger.info("Tentando fazer login...")
        try:
            # ***** DETECTE OS SELECTORS REAIS DO SEU SITE AQUI *****
            # Exemplo de seletores:
            # Campo de usuário: <input id="username" type="text">
            # Campo de senha: <input id="password" type="password">
            # Botão de login: <button id="loginButton">Entrar</button>

            # Campo de Usuário
            username_field = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "username"))  # Substitua "username" pelo ID/Name/XPath real
            )
            username_field.send_keys(username)
            apply_human_like_delays(min_delay=0.5, max_delay=1.5)

            # Campo de Senha
            password_field = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "password"))  # Substitua "password" pelo ID/Name/XPath real
            )
            password_field.send_keys(password)
            apply_human_like_delays()

            # --- Lidar com CAPTCHA na tela de Login (se houver) ---
            try:
                # Localize o elemento da imagem do CAPTCHA
                captcha_image_element = WebDriverWait(driver, 5).until(  # Curto timeout para CAPTCHA de login
                    EC.presence_of_element_located((By.ID, "captcha_img_login"))
                    # Substitua pelo ID/XPath real do CAPTCHA de login
                )
                logger.info("CAPTCHA de login detectado. Tentando resolver...")

                # Capturar o screenshot do elemento do CAPTCHA
                captcha_image_bytes = captcha_image_element.screenshot_as_png
                from io import BytesIO
                captcha_pil_image = Image.open(BytesIO(captcha_image_bytes))

                # Resolver o CAPTCHA usando a IA
                captcha_solution = solve_captcha(
                    captcha_pil_image, captcha_model, device,
                    NUM_CAPTCHA_CHARACTERS, NUM_CLASSES_PER_CHAR,
                    img_height=60, img_width=120  # Os mesmos do treinamento
                )

                # Inserir a solução no campo de CAPTCHA
                captcha_input_field = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "captcha_input_login"))
                    # Substitua pelo ID/XPath real do campo de input do CAPTCHA
                )
                captcha_input_field.send_keys(captcha_solution)
                apply_human_like_delays()

            except TimeoutException:
                logger.info("Nenhum CAPTCHA de login detectado ou demorou demais. Prosseguindo.")
            except Exception as e:
                logger.error(f"Erro ao resolver ou preencher CAPTCHA de login: {e}")
                # Decide se aborta ou continua, dependendo da criticidade do CAPTCHA de login
                return False

            # Botão de Login
            login_button = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "loginButton"))  # Substitua "loginButton" pelo ID/Name/XPath real
            )
            login_button.click()
            logger.info("Botão de login clicado.")
            apply_human_like_delays()

            # Esperar pela página pós-login ou por um elemento que indique sucesso
            WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                EC.url_changes(SITE_URL) or EC.presence_of_element_located((By.ID, "dashboard_element"))
            )
            logger.info("Login bem-sucedido (ou página pós-login carregada).")

        except TimeoutException:
            logger.error("Tempo esgotado para encontrar elementos de login ou o login falhou.")
            return False
        except NoSuchElementException as e:
            logger.error(f"Elemento de login não encontrado: {e}. Verifique os seletores.")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado durante o login: {e}")
            return False

        # --- 4. Navegar para a Página de Marcação e Esperar a Abertura de Vagas ---
        logger.info("Navegando para a página de marcação de serviços...")
        # ***** DETECTE OS SELECTORS REAIS PARA NAVEGAÇÃO E ONDE AS VAGAS APARECEM *****
        # driver.get(f"{SITE_URL}/marcar_servico") # Exemplo: Navegar diretamente
        # Ou clicar em um link:
        # service_link = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
        #     EC.element_to_be_clickable((By.LINK_TEXT, "Marcar Serviço"))
        # )
        # service_link.click()
        # apply_human_like_delays()

        # O mais crítico: esperar pelas vagas aparecerem (pontualmente às 6h)
        logger.info("Preparando para aguardar a abertura das 10 vagas...")
        start_time = time.time()

        # Loop de monitoramento para a abertura das vagas
        # Você precisará identificar um elemento na página que indica a disponibilidade das vagas.
        # Pode ser um botão que fica clicável, uma tabela que aparece, ou um texto que muda.

        # Exemplo: Esperar que um elemento de "vagas disponíveis" se torne visível/clicável
        vagas_found = False
        while time.time() - start_time < (SELENIUM_TIMEOUT * 2):  # Espera por um período maior se necessário
            try:
                # ***** SELECTOR REAL DA VAGA OU INDICADOR DE DISPONIBILIDADE *****
                # Ex: um botão que aparece e se torna clicável:
                vaga_element = driver.find_element(By.CLASS_NAME,
                                                   "available-slot-button")  # Substitua pelo seletor real
                if vaga_element.is_displayed() and vaga_element.is_enabled():
                    logger.info("Vagas detectadas e prontas para clique!")
                    vagas_found = True
                    break
                else:
                    logger.debug("Vagas ainda não disponíveis ou não clicáveis.")
            except NoSuchElementException:
                logger.debug("Elemento da vaga ainda não presente na página.")

            # Recarregar a página pode ser necessário se as vagas não atualizarem dinamicamente
            # CUIDADO: Recarregar a página pode adicionar latência crítica.
            # Se o site usa AJAX, é melhor esperar pela atualização do DOM.
            # Se for necessário recarregar, faça-o de forma estratégica e com um pequeno delay.
            # driver.refresh()
            time.sleep(0.1)  # Pequeno atraso para não sobrecarregar e dar tempo para o DOM atualizar

        if not vagas_found:
            logger.error("Tempo esgotado! Não foi possível detectar as vagas a tempo.")
            return False

        # --- 5. Tentar Clicar na Vaga (Corrida Contra o Tempo!) ---
        # Aqui, você precisa ser o mais rápido possível.
        logger.info("Tentando clicar na vaga agora mesmo!")
        try:
            # O clique deve ser o mais direto possível.
            # Se a vaga_element já foi localizada acima, clique nela.
            # Caso contrário, localize-a novamente AGORA, o mais rápido possível.
            vaga_element = WebDriverWait(driver, 2).until(  # Tempo limite bem curto para o clique
                EC.element_to_be_clickable((By.CLASS_NAME, "available-slot-button"))  # O mesmo seletor
            )
            vaga_element.click()
            logger.info("Vaga clicada com sucesso!")
            apply_human_like_delays()  # Pequeno delay após o clique

            # --- 6. Confirmar Marcação (Se houver tela de confirmação) ---
            # Pode haver uma tela de confirmação, outro CAPTCHA, etc.
            # ***** ADEQUE ESTE PASSO À LÓGICA DO SEU SITE *****
            try:
                confirmation_button = WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                    EC.element_to_be_clickable((By.ID, "confirm_booking_button"))  # Substitua pelo ID/XPath real
                )
                confirmation_button.click()
                logger.info("Marcação confirmada com sucesso!")
                apply_human_like_delays()

                # Esperar por uma mensagem de sucesso ou redirecionamento
                WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "success_message")) or
                    EC.url_contains("success")
                )
                logger.info("Processo de marcação finalizado com sucesso!")
                return True

            except TimeoutException:
                logger.warning("Nenhuma tela de confirmação ou erro. Verifique manualmente.")
                return True  # Assume sucesso se o clique principal ocorreu
            except Exception as e:
                logger.error(f"Erro durante a fase de confirmação: {e}")
                return False

        except TimeoutException:
            logger.error("Tempo esgotado para clicar na vaga.")
            return False
        except NoSuchElementException as e:
            logger.error(f"Elemento da vaga não encontrado para clique: {e}. Pode ter sido pega por outro.")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao clicar na vaga: {e}")
            return False

    except WebDriverException as e:
        logger.error(f"Erro no WebDriver (navegador travou ou fechou): {e}")
        return False
    except Exception as e:
        logger.error(f"Erro geral no processo RPA: {e}", exc_info=True)
        return False
    finally:
        quit_driver(driver)