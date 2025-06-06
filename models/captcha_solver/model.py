# sams_project/models/captcha_solver/model.py

import torch
import torch.nn as nn

class CaptchaCNN(nn.Module):
    def __init__(self, num_classes, img_height, img_width):
        super(CaptchaCNN, self).__init__()
        # Ajuste a arquitetura da CNN conforme a complexidade do seu CAPTCHA
        # Este é um exemplo básico
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), # 1 canal de entrada (graysacale)
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Reduz dimensões pela metade

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        # Calcular o tamanho da entrada para a camada linear
        # Simula uma passagem para calcular as dimensões
        # As dimensões finais dependem da altura e largura da imagem de entrada
        # e das operações de pooling.
        self._to_linear = None
        self._calc_linear_input(img_height, img_width)

        self.fc_layers = nn.Sequential(
            nn.Linear(self._to_linear, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def _calc_linear_input(self, img_height, img_width):
        # Cria um tensor de exemplo para calcular a saída das camadas convolucionais
        # A dimensão do lote (batch size) pode ser 1.
        x = torch.randn(1, 1, img_height, img_width) # 1 imagem, 1 canal, H, W
        x = self.conv_layers(x)
        self._to_linear = x[0].shape[0] * x[0].shape[1] * x[0].shape[2]

    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1) # Achata a saída para a camada linear
        x = self.fc_layers(x)
        return x

# Exemplo de uso (para demonstração, não será executado diretamente aqui)
if __name__ == "__main__":
    # Supondo CAPTCHAs de 6 caracteres, cada caractere com 36 classes (0-9, A-Z)
    # E imagens de 60x120 pixels (Altura x Largura)
    num_captcha_characters = 6
    num_classes_per_char = 36 # 0-9 e A-Z (26 letras + 10 números)
    total_output_classes = num_captcha_characters * num_classes_per_char

    img_h, img_w = 60, 120 # Exemplo: Ajuste para o tamanho real do seu CAPTCHA

    model = CaptchaCNN(total_output_classes, img_h, img_w)
    print(model)

    # Simular uma entrada
    dummy_input = torch.randn(1, 1, img_h, img_w)
    output = model(dummy_input)
    print(f"Formato da saída do modelo: {output.shape}")