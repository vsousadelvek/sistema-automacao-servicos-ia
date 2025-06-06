# sams_project/models/captcha_solver/train.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from PIL import Image
import os
from torchvision import transforms
import logging

from models.captcha_solver.model import CaptchaCNN
from config import CAPTCHA_DATA_DIR, CAPTCHA_LABELS_FILE, CAPTCHA_MODEL_PATH
from utils.logger import setup_logging

setup_logging("train_log.log", "INFO") # Log separado para o treinamento
logger = logging.getLogger(__name__)

class CaptchaDataset(Dataset):
    def __init__(self, img_dir, labels_file, transform=None):
        self.img_dir = img_dir
        self.labels_df = pd.read_csv(labels_file)
        self.transform = transform
        # Mapeamento de caracteres para índices
        self.char_to_idx = {char: i for i, char in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
        self.idx_to_char = {i: char for char, i in self.char_to_idx.items()}
        self.num_classes_per_char = len(self.char_to_idx)

    def __len__(self):
        return len(self.labels_df)

    def __getitem__(self, idx):
        img_name = self.labels_df.iloc[idx, 0]
        label_str = self.labels_df.iloc[idx, 1]
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path).convert('L') # Convert to grayscale

        if self.transform:
            image = self.transform(image)

        # Converter label string (ex: "ABC123") para um tensor de índices
        # Ex: "ABC" -> [10, 11, 12] (se A=10, B=11, C=12)
        label_indices = [self.char_to_idx[char] for char in label_str]
        label_tensor = torch.tensor(label_indices, dtype=torch.long)

        # Para modelos que preveem cada caractere individualmente, ou uma concatenação
        # Se sua CNN tem saída total de classes, transforme o label tensor para a forma correta
        # Por exemplo, se a saída é 6 * 36 classes (para 6 caracteres),
        # o target para BC12 pode ser 0 para os primeiros 36, 1 para os segundos 36, etc.
        # Isso depende da sua estratégia de perda e saída.
        # Para um Multi-label classification (com 6 outputs independentes):
        # return image, label_tensor

        # Para um único output com total_output_classes:
        # A forma mais simples para um único output da CNN:
        # Concatenar os one-hot encodings dos caracteres, ou usar um target direto
        # que a perda possa comparar.
        # Esta é uma complexidade que dependerá da sua implementação exata
        # de como a CNN fará a previsão (caractere por caractere ou string completa).
        # Para fins de exemplo, vamos assumir que o modelo prevê um tensor de `num_captcha_characters * num_classes_per_char`
        # e a perda calcula sobre isso. O target aqui precisaria ser compatível.
        # Por simplicidade, vamos usar o target como um tensor de índices.
        # No forward da CNN, a saída terá que ser reorganizada para comparar com este label_tensor.
        # Uma forma é usar CrossEntropyLoss para cada caractere e somar as perdas.
        # Para um modelo que prevê cada caractere individualmente:
        return image, label_tensor # Retorna uma imagem e um tensor de 6 índices (se 6 caracteres)


def train_model():
    logger.info("Iniciando o treinamento do modelo CAPTCHA.")

    # Hiperparâmetros
    batch_size = 64
    learning_rate = 0.001
    num_epochs = 50 # Ajuste conforme necessário

    # Tamanho esperado da imagem do CAPTCHA (ajuste para o seu caso)
    img_height, img_width = 60, 120 # Exemplo

    # Transformações para o dataset
    transform = transforms.Compose([
        transforms.Resize((img_height, img_width)),
        transforms.ToTensor(), # Converte PIL Image para Tensor, normaliza para [0, 1]
        # transforms.Normalize((0.5,), (0.5,)) # Opcional: normalização
    ])

    # Carregar o dataset
    try:
        dataset = CaptchaDataset(CAPTCHA_DATA_DIR, CAPTCHA_LABELS_FILE, transform=transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    except FileNotFoundError:
        logger.error(f"Erro: Arquivos de dados do CAPTCHA não encontrados. Verifique {CAPTCHA_DATA_DIR} e {CAPTCHA_LABELS_FILE}.")
        logger.error("Execute 'dataset_creator.py' para coletar e rotular dados primeiro.")
        return

    # Determinando o número de classes e caracteres
    num_captcha_characters = len(dataset.labels_df.iloc[0, 1]) # Assumindo todos os CAPTCHAs tem o mesmo comprimento
    num_classes_per_char = dataset.num_classes_per_char

    # Modelo, Otimizador e Função de Perda
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Usando dispositivo: {device}")

    # A arquitetura do modelo deve ser adaptada para a saída de múltiplos caracteres
    # Uma forma comum é ter uma saída para cada caractere.
    # Vamos redefinir o modelo para ter 6 saídas independentes (uma para cada caractere)
    # cada uma com `num_classes_per_char` classes.
    # No `model.py` isso seria `nn.Linear(..., num_captcha_characters * num_classes_per_char)`
    # E a função de perda teria que lidar com isso (ex: CrossEntropyLoss combinada para cada caractere)
    # Por simplicidade neste template, mantemos a saída única e o tratamento de perda seria mais complexo.
    # Alternativamente, a CNN pode ter N cabeças de saída, uma para cada caractere.
    # Para este exemplo, vou manter a `CaptchaCNN` com `total_output_classes` e adaptar a perda.
    # A maneira mais robusta seria ter 6 classificadores independentes ou uma camada de saída que é
    # remodelada para (batch_size, num_chars, num_classes_per_char)
    # Para simplificar o template, assumimos um único tensor de saída que será remodelado para cálculo de perda.
    # Isso requer um forward() um pouco mais complexo na CNN.

    # Para a CNN em model.py, a saída é `num_classes` (que é total_output_classes = num_chars * num_classes_per_char)
    # A perda deve ser calculada para cada caractere.
    # Isso geralmente significa remodelar a saída da CNN:
    # output = output.view(batch_size, num_captcha_characters, num_classes_per_char)
    # e então aplicar CrossEntropyLoss para cada caractere.

    # Criando o modelo com a saída adequada
    model = CaptchaCNN(
        num_classes=num_captcha_characters * num_classes_per_char,
        img_height=img_height,
        img_width=img_width
    ).to(device)

    # Para a função de perda, usaremos CrossEntropyLoss, mas teremos que aplicar para cada caractere.
    # A perda para cada caractere é calculada e somada.
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_accuracy = 0.0

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for i, (images, labels) in enumerate(dataloader):
            images = images.to(device)
            # Labels: (batch_size, num_captcha_characters)
            # Para comparar com a saída da CNN (batch_size, num_captcha_characters * num_classes_per_char)
            # Teremos que remodelar a saída da CNN e aplicar a perda para cada caractere.
            labels = labels.to(device) # labels são um tensor de índices (ex: [10, 11, 12, ...])

            optimizer.zero_grad()
            outputs = model(images) # (batch_size, num_captcha_characters * num_classes_per_char)

            # Remodelar a saída para calcular a perda por caractere
            outputs = outputs.view(-1, num_captcha_characters, num_classes_per_char) # (batch_size, num_chars, num_classes_per_char)
            labels = labels.view(-1, num_captcha_characters) # (batch_size, num_chars)

            # Calcular a perda para cada caractere e somar
            loss = 0
            for char_idx in range(num_captcha_characters):
                loss += criterion(outputs[:, char_idx, :], labels[:, char_idx])

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            if (i + 1) % 10 == 0:
                logger.debug(f"Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(dataloader)}], Loss: {running_loss/10:.4f}")
                running_loss = 0.0

        logger.info(f"Epoch [{epoch+1}/{num_epochs}] concluída. Média de Loss: {running_loss / len(dataloader):.4f}")

        # Avaliação (Opcional, mas recomendado para acompanhar a precisão)
        model.eval()
        correct_predictions = 0
        total_samples = 0
        with torch.no_grad():
            for images, labels in dataloader: # Usar um DataLoader de validação/teste separado
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                outputs = outputs.view(-1, num_captcha_characters, num_classes_per_char)

                # Obter as previsões para cada caractere
                _, predicted = torch.max(outputs, 2) # predicted shape: (batch_size, num_captcha_characters)

                # Comparar previsões com os rótulos verdadeiros
                # Contar quantas strings de CAPTCHA foram preditas corretamente
                correct_predictions += (predicted == labels).all(dim=1).sum().item()
                total_samples += labels.size(0)

        accuracy = (correct_predictions / total_samples) * 100
        logger.info(f"Acurácia no conjunto de treino/validação: {accuracy:.2f}%")

        # Salvar o modelo se a acurácia melhorar
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            torch.save(model.state_dict(), CAPTCHA_MODEL_PATH)
            logger.info(f"Modelo salvo com acurácia de {best_accuracy:.2f}% em {CAPTCHA_MODEL_PATH}")

    logger.info("Treinamento concluído.")

if __name__ == "__main__":
    train_model()