
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.pluggy.ai"


def main():
    client_id = os.getenv("PLUGGY_CLIENT_ID")
    client_secret = os.getenv("PLUGGY_CLIENT_SECRET")
    item_id = os.getenv("PLUGGY_ITEM_ID")

    if not all([client_id, client_secret, item_id]):
        print("Verifique as variáveis do arquivo .env.")
        return

    # 1. Autenticar na Pluggy
    auth_response = requests.post(
        f"{BASE_URL}/auth",
        json={
            "clientId": client_id,
            "clientSecret": client_secret,
        },
        timeout=30,
    )
    auth_response.raise_for_status()
    api_key = auth_response.json()["apiKey"]

    headers = {"X-API-KEY": api_key}

    # 2. Consultar as contas conectadas
    accounts_response = requests.get(
        f"{BASE_URL}/accounts",
        params={"itemId": item_id},
        headers=headers,
        timeout=30,
    )
    accounts_response.raise_for_status()

    accounts = accounts_response.json().get("results", [])
    print(f"Contas encontradas: {len(accounts)}")

    # 3. Testar o endpoint atualizado de transações
    for account in accounts:
        account_id = account["id"]

        response = requests.get(
            f"{BASE_URL}/v2/transactions",
            params={"accountId": account_id},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        transactions = data.get("results", [])

        print(
            f"Conta: {account.get('name', 'Conta')} | "
            f"Tipo: {account.get('type', 'N/A')} | "
            f"Transações nesta página: {len(transactions)} | "
            f"Há mais páginas: {'Sim' if data.get('next') else 'Não'}"
        )

    print("Teste concluído.")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as error:
        print(f"Erro HTTP: {error.response.status_code}")
        print("Confira o endpoint e as permissões da API.")
    except requests.RequestException as error:
        print(f"Erro de comunicação: {type(error).__name__}")
    except (KeyError, ValueError):
        print("A resposta da API veio em um formato inesperado.")
