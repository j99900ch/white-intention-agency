import json
import urllib.parse
import urllib.request
from pathlib import Path

env_path = Path("./white_intention/.env")

page_id = "1350090151524481"
insta_id = "17841420317966129"
token = "EAAcYJg3hnnEBSsdSc2hNVwlS6MRP2KiF3PKaaF1rGmvt8ikOfyG305ZAx19iGZB24ZB3ghbiayRhLQMF6EGMGVehqq37KWYEX2H2srvZAojy89jZCy09Y1g4ZAG4HCfD4UTRBqKDxTuSjvZCXRwOp6ZAIgUj495PF0tTZArjkKHPYSXRKx1ytlN0VvUxCQfT02LZCkb5iZC0uJGkXCAUfdwYyNqY5QZAgleJYmf5kRS8z0xC"

# 1. Update .env cleanly
lines = []
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if not any(line.startswith(k) for k in ["META_PAGE_ID=", "META_INSTAGRAM_ACCOUNT_ID=", "META_ACCESS_TOKEN="]):
                lines.append(line.rstrip("\r\n"))

lines.append(f'META_PAGE_ID="{page_id}"')
lines.append(f'META_INSTAGRAM_ACCOUNT_ID="{insta_id}"')
lines.append(f'META_ACCESS_TOKEN="{token}"')

with open(env_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("[1/2] white_intention/.env updated successfully.")

# 2. Publish announcement to Facebook Page
post_message = """🚀 Welcome to White Intention — Modern Web Architecture & Digital Acceleration.

We craft bespoke, performance-engineered websites that turn visitors into booked clients. 
Zero clunky templates. Sub-second load times. Seamless conversion flows.

👉 DM us or visit https://whiteintention.in to elevate your business presence today."""

url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
payload = urllib.parse.urlencode({"message": post_message, "access_token": token}).encode("utf-8")
req = urllib.request.Request(url, data=payload, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("\n" + "="*60)
        print("[2/2 SUCCESS] Post successfully published to Facebook Page!")
        print("Live Post ID:", res.get("id"))
        print("="*60)
except Exception as e:
    print("\n[ERROR publishing]:", e)