import os
import sys
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime

# Read credentials from Environment (Supports local .env and Cloud GitHub Secrets)
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

# 5 Daily Slots: 3 Images + 2 Videos with embedded standard background music
SLOTS = [
    # Slot 0 (09:30 AM IST) - IMAGE: Core Web Vitals & Speed
    {
        "type": "IMAGE",
        "media_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&q=80",
        "caption": """⚡ Sub-Second Speed vs. Clunky Templates.

Did you know 82% of clients leave a website if it takes more than 3 seconds to load on mobile?

At White Intention, we don't build on bloated page-builders. We engineer custom, ultra-fast web architectures with 95+ Core Web Vitals scores so you never leak valuable clients.

👉 DM us 'AUDIT' or visit https://whiteintention.in to test your current site.

#webdesign #websitedevelopment #speedoptimization #delhibusiness #whiteintention #startupindia"""
    },
    # Slot 1 (12:30 PM IST) - VIDEO REEL with Standard Background Audio: 1-Click WhatsApp Conversion
    {
        "type": "VIDEO",
        "media_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "caption": """📱 Why your website should route directly to WhatsApp in 2026.

Filling out 12-question contact forms is dead. Modern clients want immediate friction-free answers.

Every website we build at White Intention features 1-click intelligent WhatsApp routing that turns passive visitors into direct phone inquiries.

👉 Upgrade your business presence: DM us 'WHATSAPP' or visit https://whiteintention.in

#reelsindia #websitedevelopment #leadgeneration #businessgrowth #whiteintention #techagency #trendingreels"""
    },
    # Slot 2 (03:30 PM IST) - IMAGE: Zero Recurring Platform Taxes
    {
        "type": "IMAGE",
        "media_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=1080&q=80",
        "caption": """🔐 Stop paying monthly 'platform taxes' just to keep your website alive.

Most agencies lock you into proprietary platforms or charge monthly hosting markups.

The White Intention Standard:
✅ 100% Full Source Code Handover
✅ Zero recurring platform subscription lock-ins
✅ Clean, modular, scalable codebase you own forever

👉 DM us 'OWNERSHIP' or explore https://whiteintention.in

#customcode #fullstack #nowordpress #nowix #startupculture #whiteintention"""
    },
    # Slot 3 (06:30 PM IST) - VIDEO REEL with Standard Background Audio: Signature Variations (Law/Tech/Medical)
    {
        "type": "VIDEO",
        "media_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "caption": """💎 Bespoke Digital Architecture for Modern Industry Leaders.

From Corporate Authority styles for Law Firms, to Modern Tech for Startups, and Executive Strategy for Consultancies.

We engineer dark-mode, high-converting digital portals tailored to your industry caliber with built-in soundscapes and sub-second response times.

👉 Experience the difference at https://whiteintention.in or DM us for a preview.

#reelsvideo #luxurybranding #corporatewebsite #delhientrepreneurs #whiteintention #webarchitecture"""
    },
    # Slot 4 (09:30 PM IST) - IMAGE: Mobile-First Authority
    {
        "type": "IMAGE",
        "media_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1080&q=80",
        "caption": """📱 80% of your customers see you on mobile first. How does your site look?

A desktop-only website is practically invisible. White Intention designs every layout mobile-first with silky responsiveness, tactile buttons, and instant conversion flows.

Ready for a website that works 24/7 as your top salesperson?
👉 DM us 'UPGRADE' or visit https://whiteintention.in

#mobilefirst #uiux #conversionrate #landingpage #businessstrategy #whiteintention"""
    }
]

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
    slot_index = 0
    if len(sys.argv) > 1:
        try:
            slot_index = int(sys.argv[1]) % len(SLOTS)
        except ValueError:
            slot_index = 0

    item = SLOTS[slot_index]
    print(f"\n--- EXECUTING SLOT #{slot_index} [{item['type']}] ---")
    if item["type"] == "IMAGE":
        post_image(item["media_url"], item["caption"])
    else:
        post_video(item["media_url"], item["caption"])

if __name__ == "__main__":
    main()