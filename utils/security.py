# sams_project/utils/security.py

import os
import getpass  # Para input seguro de senha no console
import logging

logger = logging.getLogger(__name__)


def get_credentials_securely():
    """
    Obtém credenciais de forma segura.
    Prioriza variáveis de ambiente, depois solicita no console.
    """
    username = os.getenv("SAMS_USERNAME")
    password = os.getenv("SAMS_PASSWORD")

    if username and password:
        logger.info("Credenciais obtidas de variáveis de ambiente.")
        return username, password
    else:
        logger.warning("Credenciais não encontradas em variáveis de ambiente (SAMS_USERNAME, SAMS_PASSWORD).")
        logger.info("Por favor, digite as credenciais no console. Elas não serão exibidas.")
        try:
            username = input("Digite seu nome de usuário: ").strip()
            password = getpass.getpass("Digite sua senha: ").strip()
            if not username or not password:
                logger.error("Usuário ou senha não podem ser vazios.")
                return None, None
            logger.info("Credenciais obtidas via input do console.")
            return username, password
        except Exception as e:
            logger.error(f"Erro ao obter credenciais: {e}")
            return None, None


# Exemplo de uso
if __name__ == '__main__':
    from utils.logger import setup_logging

    setup_logging("security_test.log", "INFO")

    # Teste sem variáveis de ambiente
    print("--- Testando obtenção de credenciais (console) ---")
    u, p = get_credentials_securely()
    if u and p:
        print(f"Usuário: {u}")
        print(f"Senha (não exibida): {'*' * len(p)}")
    else:
        print("Falha ao obter credenciais.")

    # Teste com variáveis de ambiente (simule definindo-as antes de rodar este script)
    # Ex: no terminal antes de rodar:
    # set SAMS_USERNAME=teste_user
    # set SAMS_PASSWORD=teste_pass
    # python utils/security.py
    # (ou export no Linux/macOS)