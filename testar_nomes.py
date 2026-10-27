from collections import Counter
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = "https://api.pluggy.ai"


def main():
  auth = requests.post(
      f"{BASE_URL}/auth",
      json={
          "clientId": os.getenv("PLUGGY_CLIENT_ID"),
          "clientSecret": os.getenv("PLUGGY_CLIENT_SECRET"),
      },
      timeout=30,
  )
  auth.raise_for_status()
  headers = {"X-API-KEY": auth.json()["apiKey"]}

  item_id = os.getenv("PLUGGY_ITEM_ID")
  response = requests.get(
      f"{BASE_URL}/investments",
      params={"itemId": item_id, "page": 1, "pageSize": 500},
      headers=headers,
      timeout=30,
  )
  response.raise_for_status()

  investments = response.json().get("results", [])

  # --- INÍCIO DA INSPEÇÃO DE CHAVES ---
  all_keys = set()
  for inv in investments:
    all_keys.update(inv.keys())

  print("=== TODAS AS CHAVES ENCONTRADAS ===")
  for key in sorted(all_keys):
    print(f"- {key}")

  if investments:
    print("\n=== EXEMPLO DE REGISTRO COMPLETO (PRIMEIRO ITEM) ===")
    print(json.dumps(investments[0], indent=2, ensure_ascii=False))
  print("===================================================\n")
  # --- FIM DA INSPEÇÃO DE CHAVES ---

  status_counts = Counter()
  active_balance = 0.0

  for inv in investments:
    status = inv.get("status") or "SEM_STATUS"
    balance = inv.get("balance") or 0
    status_counts[status] += 1

    if status == "ACTIVE":
      active_balance += balance
      print({
          "nome": inv.get("name"),
          "instituicao": inv.get("institution"),
          "tipo": inv.get("type"),
          "subtipo": inv.get("subtype"),
          "status": status,
          "saldo": balance,
          "moeda": inv.get("currencyCode"),
          "data_referencia": inv.get("date"),
      })

  print("\nResumo por status:")
  for status, quantity in status_counts.items():
    print(f"{status}: {quantity} investimento(s)")

  print(f"Saldo dos investimentos ACTIVE: R$ {active_balance:.2f}")


if __name__ == "__main__":
  try:
    main()
  except requests.HTTPError as error:
    print(f"Erro HTTP: {error.response.status_code}")
  except requests.RequestException as error:
    print(f"Erro de comunicação: {type(error).__name__}")