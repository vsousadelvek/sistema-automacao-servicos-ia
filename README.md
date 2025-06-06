Markdown

# Sistema de Automação de Marcação de Serviços (SAMS)

Este projeto implementa um Sistema de Automação Robótica de Processos (RPA) utilizando Selenium e Inteligência Artificial (PyTorch) para automatizar a marcação de serviços em um site específico. O objetivo é contornar a limitação de vagas e a concorrência, garantindo a reserva das vagas assim que elas se tornam disponíveis.

## Visão Geral

O SAMS opera localmente no seu PC, agendado para executar em horários críticos. Ele simula a interação humana com um navegador, resolve CAPTCHAs utilizando um modelo de Rede Neural customizado, e implementa técnicas para burlar defesas anti-automação.

## Estrutura do Projeto

sams_project/
├── .venv/                     # Ambiente virtual Python
├── main.py                    # Ponto de entrada principal
├── config.py                  # Configurações do sistema
├── models/                    # Módulos e dados de IA
│   ├── captcha_solver/        # Lógica para resolver CAPTCHA com IA
│   │   ├── model.py           # Definição da arquitetura da Rede Neural
│   │   ├── train.py           # Script para treinamento do modelo
│   │   ├── predict.py         # Função para inferência (resolver CAPTCHA)
│   │   ├── dataset_creator.py # Script para coletar e rotular dados de CAPTCHA
│   │   └── trained_model.pth  # Modelo de IA treinado (salvo)
│   └── data/                  # Dados de treino para a IA do CAPTCHA
│       ├── captcha_images/    # Imagens brutas dos CAPTCHAs coletados
│       └── labels.csv         # Arquivo com as rotulações das imagens
├── rpa_core/                  # Módulo principal de automação RPA (Selenium)
│   ├── browser_manager.py     # Gerencia o navegador e opções anti-detecção
│   ├── page_interactor.py     # Funções de interação com as páginas do site
│   └── anti_detection.py      # Funções para simular comportamento humano
├── scheduler/                 # Módulo para agendamento da execução
│   └── task_scheduler.py      # Implementação do APScheduler
├── utils/                     # Funções utilitárias
│   ├── logger.py              # Configuração de logging
│   ├── notifications.py       # Funções para envio de notificações
│   └── security.py            # Funções para manipulação segura de credenciais
├── drivers/                   # Drivers do navegador (ex: chromedriver.exe)
├── requirements.txt           # Lista de dependências Python
└── README.md                  # Este arquivo


## Configuração

1.  **Clone o Repositório:** (Se estiver em um repositório Git)
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd sams_project
    ```
    Ou crie o projeto e a estrutura manualmente como feito no PyCharm.

2.  **Configurar Ambiente Virtual:**
    O PyCharm geralmente faz isso automaticamente. Se não, no terminal do projeto:
    ```bash
    python -m venv .venv
    # Para ativar (Windows):
    .venv\Scripts\activate
    # Para ativar (Linux/macOS):
    source .venv/bin/activate
    ```

3.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    Se `requirements.txt` ainda não existir, crie-o após instalar as bibliotecas essenciais:
    ```bash
    pip install selenium apscheduler opencv-python
    # Para PyTorch (CPU):
    pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
    # Ou para PyTorch (CUDA - verificar sua versão CUDA em [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)):
    # pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)
    
    # Após a instalação, gere o requirements.txt
    pip freeze > requirements.txt
    ```

4.  **Baixar Driver do Navegador:**
    Baixe o `chromedriver` (para Chrome) ou `geckodriver` (para Firefox) compatível com a versão do seu navegador. Coloque o executável na pasta `drivers/`.
    * [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
    * [GeckoDriver Downloads](https://github.com/mozilla/geckodriver/releases)

5.  **Configurar `config.py`:**
    * Atualize `SITE_URL` com o endereço do site da Priscila.
    * Ajuste `BROWSER_TYPE`, `HEADLESS_MODE` e `DRIVER_PATH` conforme sua configuração.
    * **Muito importante:** Configure `SCHEDULE_HOUR`, `SCHEDULE_MINUTE`, `SCHEDULE_SECOND` para o horário exato da abertura das vagas (ex: 6h da manhã).
    * **NÃO COLOQUE USUÁRIO E SENHA DIRETAMENTE NO `config.py`!** Use variáveis de ambiente (preferível) ou o prompt seguro.

## Uso

### 1. Coletar e Rotular Dados de CAPTCHA

Antes de treinar a IA, você precisa de um dataset de CAPTCHAs e suas respostas.

```bash
python models/captcha_solver/dataset_creator.py
Siga as instruções no console para capturar imagens de CAPTCHA e rotulá-las manualmente. Este processo é crucial para a precisão da IA e pode levar tempo.

2. Treinar o Modelo de IA
Após coletar dados suficientes e rotulá-los, treine sua Rede Neural:

Bash

python models/captcha_solver/train.py
O modelo treinado será salvo em models/captcha_solver/trained_model.pth.

3. Executar o Sistema SAMS
Para rodar o sistema e iniciar o agendador:

Bash

python main.py
O sistema irá solicitar seu nome de usuário e senha de forma segura se não estiverem definidos como variáveis de ambiente (SAMS_USERNAME, SAMS_PASSWORD). O agendador manterá o processo ativo em segundo plano até o horário agendado.

Variáveis de Ambiente para Credenciais (Recomendado):

Defina as variáveis de ambiente antes de executar main.py:

Windows (PowerShell):

PowerShell

$env:SAMS_USERNAME="seu_usuario_aqui"
$env:SAMS_PASSWORD="sua_senha_aqui"
python main.py
Linux/macOS:

Bash

export SAMS_USERNAME="seu_usuario_aqui"
export SAMS_PASSWORD="sua_senha_aqui"
python main.py
4. Monitoramento
Verifique o arquivo de log (sams_log.log definido em config.py) para acompanhar o status da execução e identificar possíveis erros.

Manutenção
Este sistema requer manutenção contínua, especialmente se o site alvo alterar sua estrutura, o tipo de CAPTCHA ou suas defesas anti-automação. Esteja preparado para:

Recoletar e rotular novos dados de CAPTCHA.
Retreinar o modelo de IA.
Atualizar a lógica de interação em rpa_core/page_interactor.py.
Ajustar as técnicas anti-detecção em rpa_core/anti_detection.py.

---

Com todos esses arquivos, você tem um ponto de partida muito robusto e organizado. Lembre-se que o maior trabalho será na **análise do site da Priscila (seletores de elementos, lógica de CAPTCHA, defesas anti-bot)** e na **coleta e rotulagem massiva de dados para a IA do CAPTCHA**.

Bom trabalho!