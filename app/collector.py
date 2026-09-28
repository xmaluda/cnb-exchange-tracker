from datetime import date
from typing import Any, Dict, List
import requests

CNB_API_URL = "https://api.cnb.cz/cnbapi/exrates/daily"
TRACKED_CURRENCIES = {"EUR", "USD", "GBP"}


def fetch_cnb_rates() -> List[Dict[str, Any]]:
    """Fetch daily exchange rates from the CNB API and filter target currencies."""
    params = {"lang": "EN"}

    try:
        response = requests.get(CNB_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        print(f"Error fetching data from CNB API: {error}")
        return []

    raw_rates = data.get("rates", [])
    filtered_rates: List[Dict[str, Any]] = []

    for item in raw_rates:
        code = item.get("currencyCode")
        if code in TRACKED_CURRENCIES:
            filtered_rates.append(
                {
                    "rate_date": item.get("validFor", str(date.today())),
                    "currency_code": code,
                    "rate": float(item.get("rate")),
                    "amount": int(item.get("amount", 1)),
                }
            )

    return filtered_rates


if __name__ == "__main__":
    rates = fetch_cnb_rates()
    print("Retrieved CNB exchange rates:")
    for r in rates:
        print(
            f"{r['amount']} {r['currency_code']} = {r['rate']} CZK (valid for: {r['rate_date']})"
        )