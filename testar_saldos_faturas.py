
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

    # Autenticação
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

    # Contas conectadas
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
        name = account.get("name", "Conta")
        account_type = account.get("type", "N/A")
        balance = account.get("balance")
        currency = account.get("currencyCode", "N/A")

        print(f"\nConta: {name} | Tipo: {account_type}")

        if balance is not None:
            print(f"Saldo informado pela API: {balance} {currency}")
        else:
            print("Saldo não informado neste resultado.")

        # Faturas: consulta apenas contas de crédito
        if account_type == "CREDIT":
            bills_response = requests.get(
                f"{BASE_URL}/bills",
                params={
                    "accountId": account_id,
                    "page": 1,
                    "pageSize": 500,
                },
                headers=headers,
                timeout=30,
            )
            bills_response.raise_for_status()
            bills_data = bills_response.json()

            print(
                "Faturas encontradas:",
                bills_data.get("total", len(bills_data.get("results", [])))
            )
            print(
                "Páginas de faturas:",
                bills_data.get("totalPages", 1)
            )

    print("\nTeste de saldos e faturas concluído.")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as error:
        print(f"Erro HTTP: {error.response.status_code}")
        print("Confira o endpoint e as permissões da API.")
    except requests.RequestException as error:
        print(f"Erro de comunicação: {type(error).__name__}")
