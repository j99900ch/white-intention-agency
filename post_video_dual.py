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

print("="*60)
print("  WHITE INTENTION - META DUAL VIDEO PUBLISHER")
print("="*60)
print(f"Target Facebook Page ID: {page_id}")
print(f"Target Instagram ID:     {ig_id}")
print("="*60)

# Sample 9:16 vertical test video (Publicly accessible MP4)
video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

caption = """🚀 Stop building slow, clunky websites in 2026.

At White Intention, we engineer custom, high-velocity digital experiences designed to convert visitors into booked clients.

👉 DM us 'WEBSITE' or visit https://whiteintention.in to elevate your business presence.

#webdesign #websitedevelopment #reelsindia #techagency #whiteintention"""

# ----------------- 1. POST VIDEO TO FACEBOOK PAGE -----------------
print("\n[1/2] Uploading video to Facebook Page...")
fb_video_url = f"https://graph.facebook.com/v21.0/{page_id}/videos"
fb_payload = urllib.parse.urlencode({
    "file_url": video_url,
    "description": caption,
    "access_token": token
}).encode("utf-8")

try:
    req = urllib.request.Request(fb_video_url, data=fb_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        fb_res = json.loads(resp.read().decode("utf-8"))
        print(f"✅ [SUCCESS] Published to Facebook! Video ID: {fb_res.get('id')}")
except Exception as e:
    print(f"❌ [FB Error]: {e}")

# ----------------- 2. POST REEL TO INSTAGRAM -----------------
print("\n[2/2] Publishing Reel to Instagram...")
ig_container_url = f"https://graph.facebook.com/v21.0/{ig_id}/media"
ig_payload = urllib.parse.urlencode({
    "media_type": "REELS",
    "video_url": video_url,
    "caption": caption,
    "share_to_feed": "true",
    "access_token": token
}).encode("utf-8")

try:
    # A. Create Reel Container
    req = urllib.request.Request(ig_container_url, data=ig_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        container_res = json.loads(resp.read().decode("utf-8"))
        container_id = container_res.get("id")
        print(f"Container created. ID: {container_id}")

    # B. Wait for Instagram to finish transcoding the video
    print("Waiting for Meta servers to process video (15 seconds)...")
    for _ in range(6):
        time.sleep(5)
        status_url = f"https://graph.facebook.com/v21.0/{container_id}?fields=status_code&access_token={token}"
        with urllib.request.urlopen(status_url) as s_resp:
            s_data = json.loads(s_resp.read().decode("utf-8"))
            status = s_data.get("status_code")
            print(f"Processing status: {status}")
            if status == "FINISHED":
                break

    # C. Publish Reel
    pub_url = f"https://graph.facebook.com/v21.0/{ig_id}/media_publish"
    pub_payload = urllib.parse.urlencode({
        "creation_id": container_id,
        "access_token": token
    }).encode("utf-8")
    
    pub_req = urllib.request.Request(pub_url, data=pub_payload, method="POST")
    with urllib.request.urlopen(pub_req) as pub_resp:
        pub_res = json.loads(pub_resp.read().decode("utf-8"))
        print(f"✅ [SUCCESS] Reel Published to Instagram! Reel Media ID: {pub_res.get('id')}")

except Exception as e:
    print(f"❌ [Instagram Error]: {e}")

print("\n" + "="*60)
print("Dual dispatch completed!")
print("="*60)