# SAMS - Sistema de Automação de Marcação de Serviços (RPA com IA Autônoma)

Este projeto implementa um **Sistema de Automação Robótica de Processos (RPA)** avançado, desenvolvido em Python, focado em otimizar a marcação de serviços em plataformas web que operam com alta concorrência e vagas limitadas (ex: agendamento de serviços com poucas vagas disponibilizadas pontualmente).

O grande diferencial do SAMS é sua **capacidade autônoma de Inteligência Artificial**, eliminando a dependência de serviços externos para resolução de desafios. Ele emprega uma **Rede Neural Convolucional (CNN)** customizada, treinada localmente com PyTorch e OpenCV, para resolver CAPTCHAs complexos com alta precisão. Além disso, incorpora técnicas avançadas de **engenharia reversa e bypass de segurança** para contornar mecanismos anti-automação (como "emcrypt" e detecções de WebDriver), garantindo uma interação fluida e indetectável com o site alvo.

O sistema opera localmente no PC do usuário, agendado para atuar em horários estratégicos (ex: segundos antes da abertura das vagas), simulando um comportamento humano otimizado para velocidade e eficiência.

## Funcionalidades Principais:

* **Automação Web Robusta:** Interação programática com navegadores via Selenium (otimizado para headless e alta performance).
* **IA Autônoma para CAPTCHA:**
    * Modelo de CNN customizado com PyTorch para resolução de CAPTCHAs baseados em imagem (letras/números).
    * Coleta e rotulagem de dataset para treinamento do modelo (processo inicial exaustivo para garantir alta precisão).
    * Persistência do modelo treinado, evitando retreinamento constante.
* **Bypass de Segurança Avançado:** Implementação de estratégias de engenharia reversa para superar scripts anti-automação e detecções de bot.
* **Agendamento Preciso:** Utilização de `APScheduler` para disparar a automação em data e hora exatas.
* **Modularidade:** Estrutura de código organizada para facilitar manutenção e escalabilidade.
* **Logging e Notificações:** Sistema de log detalhado para acompanhamento e notificações de status.

## Desafios Superados (ou Abordados):

* **Alta Concorrência:** Otimização para garantir a prioridade na aquisição de vagas limitadas.
* **Complexidade de CAPTCHA:** Desenvolvimento de IA customizada para resolver CAPTCHAs sem serviços de terceiros.
* **Defesas Anti-Automação:** Engenharia reversa e implementação de técnicas para contornar mecanismos de segurança do site.
* **Manutenção Contínua:** Reconhecimento da necessidade de adaptação a mudanças no site alvo.

Este projeto é um exemplo prático da aplicação de Inteligência Computacional e Engenharia de Software para resolver problemas de automação em cenários desafiadores.
