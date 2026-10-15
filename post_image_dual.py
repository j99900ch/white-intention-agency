import json
import time
import urllib.parse
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

page_id = cfg.get("META_PAGE_ID")
ig_id = cfg.get("META_INSTAGRAM_ACCOUNT_ID")
token = cfg.get("META_ACCESS_TOKEN")

# High-converting modern agency branding image
image_url = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&q=80"
caption = """🚀 Stop settling for slow, generic templates.

At White Intention, we build custom, high-velocity websites designed to convert visitors into booked clients.

👉 DM us 'WEBSITE' or visit https://whiteintention.in to elevate your digital presence.

#webdesign #websitedevelopment #techagency #whiteintention"""

# 1. Publish to Facebook Page (with Image)
print("\n[1/2] Publishing to Facebook Page...")
fb_url = f"https://graph.facebook.com/v21.0/{page_id}/photos"
fb_payload = urllib.parse.urlencode({
    "url": image_url,
    "caption": caption,
    "access_token": token
}).encode("utf-8")

try:
    req = urllib.request.Request(fb_url, data=fb_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"✅ [SUCCESS] Published to Facebook! Post ID: {res.get('post_id', res.get('id'))}")
except urllib.error.HTTPError as e:
    print(f"❌ [FB Error]: {e.read().decode('utf-8')}")

# 2. Publish to Instagram Feed
print("\n[2/2] Publishing Image to Instagram Feed...")
ig_url = f"https://graph.facebook.com/v21.0/{ig_id}/media"
ig_payload = urllib.parse.urlencode({
    "image_url": image_url,
    "caption": caption,
    "access_token": token
}).encode("utf-8")

try:
    req = urllib.request.Request(ig_url, data=ig_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        c_res = json.loads(resp.read().decode("utf-8"))
        c_id = c_res.get("id")
        print(f"Instagram Container ID: {c_id}")

    time.sleep(3)

    pub_url = f"https://graph.facebook.com/v21.0/{ig_id}/media_publish"
    pub_payload = urllib.parse.urlencode({"creation_id": c_id, "access_token": token}).encode("utf-8")
    pub_req = urllib.request.Request(pub_url, data=pub_payload, method="POST")
    with urllib.request.urlopen(pub_req) as p_resp:
        p_res = json.loads(p_resp.read().decode("utf-8"))
        print(f"✅ [SUCCESS] Published to Instagram! Media ID: {p_res.get('id')}")

except urllib.error.HTTPError as e:
    print(f"❌ [Instagram Error]: {e.read().decode('utf-8')}")