import os
import sys
import json
import time
import random
import urllib.parse
import urllib.request
from datetime import datetime

# Read credentials from Environment or local .env
PAGE_ID = os.getenv("META_PAGE_ID", "1350090151524481")
IG_ID = os.getenv("META_INSTAGRAM_ACCOUNT_ID", "17841420317966129")
TOKEN = os.getenv("META_ACCESS_TOKEN", "")

if not TOKEN:
    env_file = "./white_intention/.env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("META_ACCESS_TOKEN="):
                    TOKEN = line.split("=", 1)[1].strip('"').strip("'")

# ----------------- DYNAMIC COPY GENERATION MATRICES -----------------
HOOKS_IMAGE = [
    "🚨 Your website isn't struggling with traffic. It's leaking trust.",
    "⚡ Why 82% of high-ticket clients leave a website within the first 3 seconds.",
    "🛑 Stop paying monthly platform subscriptions just to keep your own website online.",
    "📱 If your business website is not built mobile-first, it is practically invisible.",
    "💡 The difference between a ₹10k template and a high-converting web architecture."
]

BODY_POINTS = [
    "Most business websites are weighed down by bloated plugins, slow server responses, and cluttered layouts that frustrate prospective clients.\n\nAt White Intention, we engineer custom web applications from the ground up:\n• Sub-second Core Web Vitals performance\n• Clean, modern dark-mode corporate aesthetics\n• Direct 1-click WhatsApp inquiry funnels\n• 100% Source code ownership with zero monthly platform lock-ins.",
    "When a corporate client or clinic patient clicks your link on Instagram or Google, they evaluate your credibility immediately on mobile.\n\nWhite Intention delivers performance-engineered digital platforms designed specifically around your customer's conversion journey.",
    "Why settle for generic cookie-cutter templates that look identical to 500 competitors?\n\nWhite Intention crafts bespoke web experiences tailored for clinics, corporate firms, and growing brands that want to command premium authority."
]

CTAS = [
    "👉 DM us 'AUDIT' or visit https://whiteintention.in to get a free website speed & UX audit.",
    "👉 Ready to turn visitors into booked inquiries? Message us 'UPGRADE' or visit https://whiteintention.in",
    "👉 Explore our client case studies and modern designs at https://whiteintention.in — or DM us for a preview."
]

HASHTAGS = [
    "#webdesign #websitedevelopment #customwebsite #startupindia #delhibusiness #entrepreneurship #landingpagedesign #whiteintention #nowordpress #b2bmarketing",
    "#techagency #webarchitecture #uiuxdesign #conversionrate #mobilefirst #modernweb #businessgrowthindia #delhientrepreneurs #whiteintention",
    "#fullstackdeveloper #codingagency #cleancode #luxurybranding #corporatewebsite #whiteintention #digitalgrowth"
]

# Media asset pools (9:16 vertical videos with audio & high-res images)
IMAGE_POOL = [
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&q=80",
    "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=1080&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1080&q=80",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1080&q=80",
    "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1080&q=80"
]

VIDEO_POOL = [
    # Fast-start MP4s with audio
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
]

def generate_unique_content(is_video=False):
    hook = random.choice(HOOKS_IMAGE)
    body = random.choice(BODY_POINTS)
    cta = random.choice(CTAS)
    tags = random.choice(HASHTAGS)
    
    caption = f"{hook}\n\n{body}\n\n{cta}\n\n{tags}"
    media_url = random.choice(VIDEO_POOL) if is_video else random.choice(IMAGE_POOL)
    return media_url, caption

# ----------------- PUBLISHING FUNCTIONS -----------------
def post_image(url, caption):
    print("Publishing Image to Facebook Page...")
    fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
    fb_payload = urllib.parse.urlencode({"url": url, "caption": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(fb_url, data=fb_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        fb_res = json.loads(resp.read().decode("utf-8"))
        print(f"✅ Facebook Image Posted! ID: {fb_res.get('post_id', fb_res.get('id'))}")

    print("Publishing Image to Instagram Feed...")
    ig_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media"
    ig_payload = urllib.parse.urlencode({"image_url": url, "caption": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(ig_url, data=ig_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        c_id = json.loads(resp.read().decode("utf-8")).get("id")

    time.sleep(3)
    pub_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media_publish"
    pub_payload = urllib.parse.urlencode({"creation_id": c_id, "access_token": TOKEN}).encode("utf-8")
    pub_req = urllib.request.Request(pub_url, data=pub_payload, method="POST")
    with urllib.request.urlopen(pub_req) as p_resp:
        ig_res = json.loads(p_resp.read().decode("utf-8"))
        print(f"✅ Instagram Image Live! ID: {ig_res.get('id')}")

def post_video(url, caption):
    print("Publishing Video to Facebook Page...")
    fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
    fb_payload = urllib.parse.urlencode({"file_url": url, "description": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(fb_url, data=fb_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        fb_res = json.loads(resp.read().decode("utf-8"))
        print(f"✅ Facebook Video Live! ID: {fb_res.get('id')}")

    print("Publishing Reel with Audio to Instagram...")
    ig_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media"
    ig_payload = urllib.parse.urlencode({"media_type": "REELS", "video_url": url, "caption": caption, "share_to_feed": "true", "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(ig_url, data=ig_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        c_id = json.loads(resp.read().decode("utf-8")).get("id")

    print("Meta transcoding video + audio stream...")
    for _ in range(12):
        time.sleep(5)
        st_url = f"https://graph.facebook.com/v21.0/{c_id}?fields=status_code&access_token={TOKEN}"
        with urllib.request.urlopen(st_url) as s_resp:
            status = json.loads(s_resp.read().decode("utf-8")).get("status_code")
            print(f"Status: {status}")
            if status == "FINISHED":
                break

    pub_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media_publish"
    pub_payload = urllib.parse.urlencode({"creation_id": c_id, "access_token": TOKEN}).encode("utf-8")
    pub_req = urllib.request.Request(pub_url, data=pub_payload, method="POST")
    with urllib.request.urlopen(pub_req) as p_resp:
        ig_res = json.loads(p_resp.read().decode("utf-8"))
        print(f"✅ Instagram Reel with Audio Live! ID: {ig_res.get('id')}")

def main():
    # Slot rule: 5 slots per day
    # Slot 0: Image (9:30 AM IST)
    # Slot 1: Video Reel (12:30 PM IST)
    # Slot 2: Image (3:30 PM IST)
    # Slot 3: Video Reel (6:30 PM IST)
    # Slot 4: Image (9:30 PM IST)
    slot_index = 0
    if len(sys.argv) > 1:
        try:
            slot_index = int(sys.argv[1]) % 5
        except ValueError:
            slot_index = 0

    is_video = (slot_index in [1, 3])
    media_url, caption = generate_unique_content(is_video)

    print(f"\n=======================================================")
    print(f"EXECUTING DAILY SLOT #{slot_index} [{'VIDEO REEL' if is_video else 'IMAGE POST'}]")
    print(f"=======================================================")
    print(f"Generated Caption:\n{caption}\n")

    if is_video:
        post_video(media_url, caption)
    else:
        post_image(media_url, caption)

if __name__ == "__main__":
    main()