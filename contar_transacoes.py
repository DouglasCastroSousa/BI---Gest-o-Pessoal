
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
        raise SystemExit("Confira as variáveis do arquivo .env.")

    auth = requests.post(
        f"{BASE_URL}/auth",
        json={
            "clientId": client_id,
            "clientSecret": client_secret,
        },
        timeout=30,
    )
    auth.raise_for_status()
    headers = {"X-API-KEY": auth.json()["apiKey"]}

    response = requests.get(
        f"{BASE_URL}/accounts",
        params={"itemId": item_id},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    accounts = response.json().get("results", [])

    for account in accounts:
        account_id = account["id"]
        total = 0
        url = f"{BASE_URL}/v2/transactions"
        params = {"accountId": account_id}
        pages = 0

        while url:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            total += len(data.get("results", []))
            pages += 1

            next_page = data.get("next")
            if next_page:
                # A Pluggy fornece a query pronta para a próxima página.
                url = f"{BASE_URL}/v2/transactions{next_page}"
                params = None
            else:
                url = None

        print(
            f"Conta: {account.get('name', 'Conta')} | "
            f"Páginas consultadas: {pages} | "
            f"Total de transações: {total}"
        )

    print("Contagem concluída.")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as error:
        print(f"Erro HTTP: {error.response.status_code}")
    except requests.RequestException as error:
        print(f"Erro de comunicação: {type(error).__name__}")
