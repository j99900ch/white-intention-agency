import json
import urllib.request
from pathlib import Path

env_path = Path("./white_intention/.env")
cfg = {}
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")

token = cfg.get("META_ACCESS_TOKEN")
container_id = "18131375521677266"

# Query the status and error details from the container you just created
url = f"https://graph.facebook.com/v21.0/{container_id}?fields=status_code,status&access_token={token}"
try:
    with urllib.request.urlopen(url) as resp:
        print("Meta Container Diagnostic:", json.loads(resp.read().decode("utf-8")))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.read().decode("utf-8"))