# sams_project/rpa_core/anti_detection.py

import time
import random
import logging

logger = logging.getLogger(__name__)

def apply_human_like_delays(min_delay=0.5, max_delay=1.5):
    """
    Aplica um atraso aleatório para simular um comportamento humano.
    Útil entre cliques, preenchimentos de campo, etc.
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    logger.debug(f"Atraso aplicado: {delay:.2f} segundos.")

def simulate_typing_speed(element, text, min_delay=0.05, max_delay=0.15):
    """
    Simula digitação lenta, caractere por caractere.
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))
    logger.debug(f"Texto digitado com atraso: '{text}'")

def simulate_mouse_movement(driver):
    """
    Simula movimentos do mouse aleatórios na tela.
    Isso é mais complexo e pode ser feito com ActionChains do Selenium.
    Será implementado se for necessário para burlar detecções avançadas.
    """
    # Exemplo: mover o mouse para uma posição aleatória na tela
    # e clicar (ou não)
    # from selenium.webdriver.common.action_chains import ActionChains
    # actions = ActionChains(driver)
    # x_offset = random.randint(0, driver.execute_script("return window.innerWidth;"))
    # y_offset = random.randint(0, driver.execute_script("return window.innerHeight;"))
    # actions.move_by_offset(x_offset, y_offset).perform()
    # logger.debug(f"Movimento de mouse simulado para ({x_offset}, {y_offset}).")
    pass # Placeholder por enquanto