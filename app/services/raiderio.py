import requests

RAIDERIO_BASE = "https://raider.io/api/v1"

def get_character(region: str, realm: str, name: str) -> dict:
    url = f"{RAIDERIO_BASE}/characters/profile"
    params = {
        "region": region,
        "realm": realm,
        "name": name,
        "fields": "mythic_plus_scores_by_season:current,mythic_plus_recent_runs",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
