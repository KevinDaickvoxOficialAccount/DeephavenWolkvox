import os

WOLKVOX_SERVER = os.environ.get("WOLKVOX_SERVER", "").strip()
WOLKVOX_TOKEN  = os.environ.get("WOLKVOX_TOKEN", "").strip()
POLL_SECONDS   = int(os.environ.get("POLL_SECONDS", "60"))

BASE_URL = f"https://wv{WOLKVOX_SERVER}.wolkvox.com/api/v2/real_time.php"
URL_AGENTES  = f"{BASE_URL}?api=agents"
URL_LATENCIA = f"{BASE_URL}?api=latency"

HEADERS = {
    "wolkvox_server": WOLKVOX_SERVER,   # <- requerido por tu doc
    "wolkvox-token": WOLKVOX_TOKEN,
}