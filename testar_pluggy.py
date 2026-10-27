
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.pluggy.ai"

client_id = os.getenv("PLUGGY_CLIENT_ID")
client_secret = os.getenv("PLUGGY_CLIENT_SECRET")
item_id = os.getenv("PLUGGY_ITEM_ID")

if not all([client_id, client_secret, item_id]):
    raise SystemExit(
        "Configure PLUGGY_CLIENT_ID, PLUGGY_CLIENT_SECRET "
        "e PLUGGY_ITEM_ID no arquivo .env."
    )

try:
    auth = requests.post(
        f"{BASE_URL}/auth",
        json={
            "clientId": client_id,
            "clientSecret": client_secret,
        },
        timeout=30,
    )
    auth.raise_for_status()
    api_key = auth.json()["apiKey"]

    response = requests.get(
        f"{BASE_URL}/accounts",
        params={"itemId": item_id},
        headers={"X-API-KEY": api_key},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    accounts = data.get("results", []) if isinstance(data, dict) else data

    print(f"Consulta realizada. Contas encontradas: {len(accounts)}")

    for account in accounts:
        print({
            "nome": account.get("name"),
            "tipo": account.get("type"),
            "moeda": account.get("currencyCode"),
        })

except requests.HTTPError as e:
    print("A API retornou um erro HTTP:", e.response.status_code)
    print("Verifique as credenciais, o itemId e as permissões.")
except requests.RequestException as e:
    print("Falha de comunicação com a API:", type(e).__name__)
except (KeyError, ValueError):
    print("A resposta da API não veio no formato esperado.")
