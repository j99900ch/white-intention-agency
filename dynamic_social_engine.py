import os
import sys
import json
import time
import random
import urllib.parse
import urllib.request

PAGE_ID = os.getenv("META_PAGE_ID", "").strip()
IG_ID = os.getenv("META_INSTAGRAM_ACCOUNT_ID", "").strip()
TOKEN = os.getenv("META_ACCESS_TOKEN", "").strip()

print(f"Auth check: PAGE_ID present? {bool(PAGE_ID)}, IG_ID present? {bool(IG_ID)}, TOKEN present? {bool(TOKEN)}")

if not all([PAGE_ID, IG_ID, TOKEN]):
    print("ERROR: One or more Meta secrets are missing from GitHub Secrets.")
    sys.exit(1)

HOOKS = [
    "🚨 Your website isn't struggling with traffic. It's leaking trust.",
    "⚡ Why 82% of high-ticket clients leave a website within the first 3 seconds.",
    "🛑 Stop paying monthly platform subscriptions just to keep your own website online.",
    "📱 If your business website is not built mobile-first, it is practically invisible."
]

BODIES = [
    "Most business websites are weighed down by bloated plugins, slow server responses, and cluttered layouts.\n\nAt White Intention, we engineer custom web applications from the ground up:\n• Sub-second Core Web Vitals performance\n• Clean, modern dark-mode corporate aesthetics\n• Direct 1-click WhatsApp inquiry funnels\n• 100% Source code ownership.",
    "When a corporate client or clinic patient clicks your link on Instagram or Google, they evaluate your credibility immediately on mobile.\n\nWhite Intention delivers performance-engineered digital platforms designed specifically around your customer's conversion journey."
]

CTAS = [
    "👉 DM us 'AUDIT' or visit https://whiteintention.in to get a free website speed & UX audit.",
    "👉 Ready to turn visitors into booked inquiries? Message us 'UPGRADE' or visit https://whiteintention.in"
]

TAGS = "#webdesign #websitedevelopment #customwebsite #startupindia #delhibusiness #entrepreneurship #landingpagedesign #whiteintention #nowordpress"

IMAGE_POOL = [
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&q=80",
    "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=1080&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1080&q=80"
]

VIDEO_POOL = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
]

def post_facebook_image(url, caption):
    print("\n--- Posting Image to Facebook Page ---")
    fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
    data = urllib.parse.urlencode({"url": url, "caption": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(fb_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print("✅ Facebook Image Published! ID:", res.get("id", res.get("post_id")))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print("❌ Facebook API Error:", err_msg)
    except Exception as e:
        print("❌ Facebook Unexpected Error:", e)

def post_instagram_image(url, caption):
    print("\n--- Posting Image to Instagram Feed ---")
    ig_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media"
    data = urllib.parse.urlencode({"image_url": url, "caption": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(ig_url, data=data, method="POST")
    c_id = None
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            c_id = res.get("id")
            print(f"Container Created: {c_id}")
    except urllib.error.HTTPError as e:
        print("❌ Instagram Container Error:", e.read().decode("utf-8"))
        return
    except Exception as e:
        print("❌ Instagram Container Unexpected Error:", e)
        return

    time.sleep(5)
    pub_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media_publish"
    pub_data = urllib.parse.urlencode({"creation_id": c_id, "access_token": TOKEN}).encode("utf-8")
    pub_req = urllib.request.Request(pub_url, data=pub_data, method="POST")
    try:
        with urllib.request.urlopen(pub_req) as pub_resp:
            res = json.loads(pub_resp.read().decode("utf-8"))
            print("✅ Instagram Image Published! ID:", res.get("id"))
    except urllib.error.HTTPError as e:
        print("❌ Instagram Publish Error:", e.read().decode("utf-8"))
    except Exception as e:
        print("❌ Instagram Publish Unexpected Error:", e)

def post_facebook_video(url, caption):
    print("\n--- Posting Video to Facebook Page ---")
    fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
    data = urllib.parse.urlencode({"file_url": url, "description": caption, "access_token": TOKEN}).encode("utf-8")
    req = urllib.request.Request(fb_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print("✅ Facebook Video Published! ID:", res.get("id"))
    except urllib.error.HTTPError as e:
        print("❌ Facebook Video Error:", e.read().decode("utf-8"))
    except Exception as e:
        print("❌ Facebook Video Unexpected Error:", e)

def post_instagram_reel(url, caption):
    print("\n--- Posting Reel with Audio to Instagram ---")
    ig_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media"
    data = urllib.parse.urlencode({
        "media_type": "REELS",
        "video_url": url,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": TOKEN
    }).encode("utf-8")
    req = urllib.request.Request(ig_url, data=data, method="POST")
    c_id = None
    try:
        with urllib.request.urlopen(req) as resp:
            c_id = json.loads(resp.read().decode("utf-8")).get("id")
            print(f"Reel Container Created: {c_id}")
    except urllib.error.HTTPError as e:
        print("❌ Instagram Reel Container Error:", e.read().decode("utf-8"))
        return
    except Exception as e:
        print("❌ Instagram Reel Container Unexpected Error:", e)
        return

    print("Transcoding on Meta cloud...")
    for _ in range(12):
        time.sleep(5)
        st_url = f"https://graph.facebook.com/v21.0/{c_id}?fields=status_code&access_token={TOKEN}"
        try:
            with urllib.request.urlopen(st_url) as s_resp:
                status = json.loads(s_resp.read().decode("utf-8")).get("status_code")
                print(f"Transcoding status: {status}")
                if status == "FINISHED":
                    break
        except Exception as e:
            print("Status poll error:", e)

    pub_url = f"https://graph.facebook.com/v21.0/{IG_ID}/media_publish"
    pub_data = urllib.parse.urlencode({"creation_id": c_id, "access_token": TOKEN}).encode("utf-8")
    pub_req = urllib.request.Request(pub_url, data=pub_data, method="POST")
    try:
        with urllib.request.urlopen(pub_req) as p_resp:
            res = json.loads(p_resp.read().decode("utf-8"))
            print("✅ Instagram Reel Published! ID:", res.get("id"))
    except urllib.error.HTTPError as e:
        print("❌ Instagram Reel Publish Error:", e.read().decode("utf-8"))
    except Exception as e:
        print("❌ Instagram Reel Publish Unexpected Error:", e)

def main():
    slot_index = 0
    if len(sys.argv) > 1:
        try:
            slot_index = int(sys.argv[1]) % 5
        except ValueError:
            slot_index = 0

    is_video = (slot_index in [1, 3])
    caption = f"{random.choice(HOOKS)}\n\n{random.choice(BODIES)}\n\n{random.choice(CTAS)}\n\n{TAGS}"
    
    print("=" * 60)
    print(f"EXECUTING DAILY SLOT #{slot_index} [{'VIDEO REEL' if is_video else 'IMAGE POST'}]")
    print("=" * 60)
    print(f"Generated Caption:\n{caption}\n")

    if is_video:
        vid_url = random.choice(VIDEO_POOL)
        post_facebook_video(vid_url, caption)
        post_instagram_reel(vid_url, caption)
    else:
        img_url = random.choice(IMAGE_POOL)
        post_facebook_image(img_url, caption)
        post_instagram_image(img_url, caption)

    print("\nSlot processing finished.")

if __name__ == "__main__":
    main()