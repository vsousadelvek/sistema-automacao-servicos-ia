# sams_project/models/captcha_solver/predict.py

import torch
from PIL import Image
from torchvision import transforms
import logging
import os
from models.captcha_solver.model import CaptchaCNN
from config import CAPTCHA_MODEL_PATH
from models.captcha_solver.train import CaptchaDataset # Para acessar char_to_idx/idx_to_char

logger = logging.getLogger(__name__)

def load_captcha_model(num_captcha_characters, num_classes_per_char, img_height, img_width):
    """Carrega o modelo de CNN treinado."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CaptchaCNN(
        num_classes=num_captcha_characters * num_classes_per_char,
        img_height=img_height,
        img_width=img_width
    ).to(device)
    try:
        model.load_state_dict(torch.load(CAPTCHA_MODEL_PATH, map_location=device))
        model.eval() # Coloca o modelo em modo de avaliação
        logger.info(f"Modelo CAPTCHA carregado com sucesso de {CAPTCHA_MODEL_PATH}")
        return model, device
    except FileNotFoundError:
        logger.error(f"Erro: Modelo CAPTCHA não encontrado em {CAPTCHA_MODEL_PATH}. Treine o modelo primeiro.")
        return None, None
    except Exception as e:
        logger.error(f"Erro ao carregar o modelo CAPTCHA: {e}")
        return None, None

def solve_captcha(image_path_or_pil_image, model, device, num_captcha_characters, num_classes_per_char, img_height, img_width):
    """
    Resolve um CAPTCHA usando o modelo de IA carregado.
    Aceita caminho de imagem ou objeto PIL Image.
    """
    if isinstance(image_path_or_pil_image, str):
        image = Image.open(image_path_or_pil_image).convert('L') # Grayscale
    else: # Assumimos que é um objeto PIL Image
        image = image_path_or_pil_image.convert('L')

    transform = transforms.Compose([
        transforms.Resize((img_height, img_width)),
        transforms.ToTensor(),
        # transforms.Normalize((0.5,), (0.5,)) # Use a mesma normalização do treinamento
    ])

    image_tensor = transform(image).unsqueeze(0).to(device) # Adiciona dimensão de batch

    with torch.no_grad():
        output = model(image_tensor)
        # Remodelar a saída para prever cada caractere
        output = output.view(-1, num_captcha_characters, num_classes_per_char) # (1, num_chars, num_classes_per_char)
        _, predicted_indices = torch.max(output, 2) # (1, num_chars)

    # Converte os índices previstos de volta para caracteres
    # Criamos um CaptchaDataset dummy para acessar o idx_to_char
    dummy_dataset = CaptchaDataset("", "", transform=None) # Sem arquivos, só para mapeamento
    predicted_captcha = "".join([dummy_dataset.idx_to_char[idx.item()] for idx in predicted_indices[0]])

    logger.info(f"CAPTCHA resolvido: {predicted_captcha}")
    return predicted_captcha

# Exemplo de uso (para teste, não será executado diretamente no fluxo principal da RPA)
if __name__ == "__main__":
    # Estes parâmetros devem corresponder aos usados no treinamento
    NUM_CAPTCHA_CHARACTERS = 6
    NUM_CLASSES_PER_CHAR = len("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ") # 36
    IMG_H, IMG_W = 60, 120

    # Carregar o modelo
    loaded_model, device = load_captcha_model(
        num_captcha_characters=NUM_CAPTCHA_CHARACTERS,
        num_classes_per_char=NUM_CLASSES_PER_CHAR,
        img_height=IMG_H,
        img_width=IMG_W
    )

    if loaded_model:
        # Crie um arquivo de imagem de CAPTCHA de teste para esta demonstração
        # Exemplo: create_dummy_captcha_image("test_captcha.png", "ABC123", 60, 120)
        test_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'test_captcha.png')
        if os.path.exists(test_image_path):
            predicted_value = solve_captcha(test_image_path, loaded_model, device,
                                            NUM_CAPTCHA_CHARACTERS, NUM_CLASSES_PER_CHAR, IMG_H, IMG_W)
            print(f"Previsão para {os.path.basename(test_image_path)}: {predicted_value}")
        else:
            print(f"Arquivo de teste '{test_image_path}' não encontrado. Crie um para testar.")