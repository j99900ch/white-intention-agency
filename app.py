import os
import sys
import json
import sqlite3
import urllib.parse
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "white_intention" / "storage"
PREVIEWS_DIR = STORAGE_DIR / "previews"
DB_PATH = STORAGE_DIR / "agency.db"
ENV_PATH = BASE_DIR / "white_intention" / ".env"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

# ----------------- CONFIG LOADER -----------------
def get_config():
    cfg = {
        "AGENCY_NAME": "White Intention",
        "AGENCY_TAGLINE": "AI-Powered Website Design, Development & Modernization",
        "AGENCY_CONTACT_EMAIL": "chaudharyjyoti0754@gmail.com",
        "GPAY_UPI_ID": "chaudharyjyoti0754@oksbi",
        "GPAY_PAYEE_NAME": "White Intention",
        "GPAY_BENEFICIARY_NAME": "Jyoti Chaudhary",
    }
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg

# ----------------- DATABASE -----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        industry TEXT,
        website_url TEXT,
        contact_channel TEXT,
        contact_value TEXT,
        raw_requirements TEXT,
        analyzed_insights TEXT,
        recommended_tier TEXT,
        status TEXT DEFAULT "discovered",
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        tier_selected TEXT,
        base_price_inr REAL,
        custom_features TEXT,
        custom_surcharge_inr REAL DEFAULT 0,
        proposed_price_inr REAL,
        project_scope TEXT,
        quote_approved_by_owner INTEGER DEFAULT 0,
        payment_status TEXT DEFAULT "pending",
        payment_verified_by_owner INTEGER DEFAULT 0,
        delivery_status TEXT DEFAULT "pending",
        delivery_approved_by_owner INTEGER DEFAULT 0,
        preview_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(lead_id) REFERENCES leads(id)
    )
    ''')
    conn.commit()
    conn.close()

# ----------------- UPGRADED PRICING TIERS -----------------
TIERS = {
    "1": {
        "name": "Basic",
        "range_label": "₹20,000 – ₹30,000",
        "default_base": 20000.0,
        "max_base": 30000.0,
        "summary": "High-Velocity 3-Page Conversion Foundation",
        "features": [
            "Ultra-clean mobile-first responsive architecture",
            "Direct Value-Proposition Hero Banner & Trust Elements",
            "1-Click Floating WhatsApp Conversion Button",
            "Core Services & Credibility Showcase Matrix",
            "Interactive Contact & Lead Capture Form",
            "Standard On-page SEO setup & Speed optimization"
        ]
    },
    "2": {
        "name": "Average Level",
        "range_label": "₹35,000 – ₹40,000",
        "default_base": 35000.0,
        "max_base": 40000.0,
        "summary": "Full Business Authority & Client Acquisition Engine",
        "features": [
            "5 to 7 Comprehensive Corporate Layout Pages",
            "Interactive Service Grids with Dynamic Hover Feedback",
            "Client Case Study & Testimonial Proof Carousel",
            "Smart Lead Qualification Diagnostic Form",
            "Local Schema, Microdata & Semantic SEO Integration",
            "Multi-channel Direct Routing (Email + WhatsApp Lead Sync)"
        ]
    },
    "3": {
        "name": "Advance Level",
        "range_label": "₹45,000 – ₹60,000+",
        "default_base": 45000.0,
        "max_base": 60000.0,
        "summary": "Enterprise High-Ticket Digital Funnel & Dynamic Platform",
        "features": [
            "Multi-page Bespoke High-Ticket Conversion Architecture",
            "Dynamic Pricing / Custom Quote Estimator Modal",
            "Automated Consultation / Patient Scheduler Embed Hook",
            "Trust & Social Proof Validation Banners",
            "Advanced Micro-animations & Tailwind Glassmorphic Accents",
            "VIP Priority Deployment + 30-Day Technical Maintenance"
        ]
    }
}

KNOWN_CUSTOM_KEYWORDS = [
    "payment gateway", "razorpay", "stripe", "ecommerce", "cart",
    "portal", "dashboard", "login", "auth", "membership",
    "multilingual", "multi language", "hindi", "spanish",
    "ai bot", "chatbot", "crm", "erp", "inventory", "sms", "database sync",
    "booking system", "calculator"
]

def analyze_customer_requirements(business_name: str, industry: str, raw_req: str):
    analysis = {}
    analysis["core_problem"] = f"Client operates in '{industry}' where prospect trust and immediate friction-free contact decide 80% of sales conversions."
    analysis["ux_strategy"] = "Deploy above-the-fold psychological proof points, friction-free WhatsApp CTA, and clear problem-solution contrast."
    
    req_lower = raw_req.lower()
    
    detected_custom = []
    for kw in KNOWN_CUSTOM_KEYWORDS:
        if kw in req_lower:
            detected_custom.append(kw)
    analysis["detected_custom"] = detected_custom

    if any(k in req_lower for k in ["booking", "schedule", "quote", "calculator", "premium", "luxury", "advance", "enterprise", "funnel", "portal", "custom"]) or len(detected_custom) > 1:
        rec = "3"
        rationale = "Customer requires Advance Level platform (₹45,000 - ₹60,000+) due to specialized automation, multi-feature workflows, or high-ticket branding."
    elif any(k in req_lower for k in ["leads", "growth", "seo", "services", "average", "portfolio", "cases", "corporate"]):
        rec = "2"
        rationale = "Customer needs Average Level platform (₹35,000 - ₹40,000) for full corporate authority and multi-page lead capture."
    else:
        rec = "1"
        rationale = "Customer needs Basic platform (₹20,000 - ₹30,000) for clean, fast mobile conversion without unnecessary complexity."

    analysis["recommended_tier"] = rec
    analysis["rationale"] = rationale
    return analysis

# ----------------- WORKFLOW ACTIONS -----------------
def add_and_analyze_lead():
    print("\n" + "="*68)
    print("      [200-IQ LEAD INGESTION & REQUIREMENT ANALYZER]")
    print("="*68)
    name = input("Business Name: ").strip()
    industry = input("Industry / Niche (e.g., Dental Clinic, Corporate Law, Real Estate): ").strip()
    site = input("Current Website or Social URL: ").strip()
    channel = input("Outreach Channel (Instagram / Email / LinkedIn / WhatsApp): ").strip()
    contact = input("Contact Handle / Email / Phone: ").strip()
    raw_req = input("Client's Stated Requirements / Pain Points: ").strip()

    if not name:
        print("[!] Business name required.")
        return

    insights = analyze_customer_requirements(name, industry, raw_req)
    rec_tier_key = insights["recommended_tier"]
    rec_tier = TIERS[rec_tier_key]

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO leads (business_name, industry, website_url, contact_channel, contact_value, raw_requirements, analyzed_insights, recommended_tier, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, "analyzed")
    ''', (name, industry, site, channel, contact, raw_req, json.dumps(insights), rec_tier["name"]))
    lead_id = cur.lastrowid
    conn.commit()
    conn.close()

    print("\n" + "*"*68)
    print("                 WHITE INTENTION DEEP DIAGNOSTIC")
    print("*"*68)
    print(f"Lead ID:              #{lead_id} - {name} ({industry})")
    print(f"Strategic Diagnosis:  {insights['core_problem']}")
    print(f"UX/Conversion Play:   {insights['ux_strategy']}")
    print(f"Recommended Tier:     Tier {rec_tier_key} - {rec_tier['name']} ({rec_tier['range_label']})")
    if insights["detected_custom"]:
        print(f"⚡ Special Features Detected: {', '.join(insights['detected_custom'])} (Will scale price within/beyond tier)")
    print(f"Architectural Reason: {insights['rationale']}")
    print("*"*68)

    cfg = get_config()
    print("\n" + "="*60)
    print("PROPOSED HIGH-IQ SOFT OUTREACH INTRO (READY TO SEND):")
    print("="*60)
    print(f"Hi {name} Team,\n")
    print(f"I came across your business while analyzing established brands in the {industry} space.")
    print(f"We noticed an opportunity to elevate your digital presence, client conversion flow, and brand authority.\n")
    print(f"At {cfg['AGENCY_NAME']}, we architect and build bespoke, high-performance websites engineered to turn visitors into booked clients.\n")
    print(f"We've analyzed your specific requirements and mapped a tailored blueprint. Would you be open to reviewing a concept preview? No pressure at all.\n")
    print(f"Best regards,\n{cfg['AGENCY_NAME']} Team\nhttps://whiteintention.in")
    print("="*60)

def draft_tiered_quote():
    print("\n--- [STEP 2] DRAFT QUOTATION (WITH ADVANCED TIER PRICING) ---")
    lead_id = input("Enter Lead ID: ").strip()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    lead = cur.fetchone()
    conn.close()

    if not lead:
        print("[!] Lead not found.")
        return

    print(f"\nConfiguring quotation for: {lead['business_name']} ({lead['industry']})")
    print(f"Client Requirements: {lead['raw_requirements']}")
    print("-" * 65)
    print("Select Package Level:")
    print("1. Basic Level   - ₹20,000 – ₹30,000 (3-page conversion foundation)")
    print("2. Average Level - ₹35,000 – ₹40,000 (5-7 page authority & lead engine)")
    print("3. Advance Level - ₹45,000 – ₹60,000+ (Full high-ticket funnel & custom logic)")
    tier_choice = input("Select Tier (1, 2, or 3): ").strip()

    if tier_choice not in TIERS:
        print("[!] Invalid tier selected.")
        return

    selected = TIERS[tier_choice]
    
    # Base Price Prompt within the Tier's Window
    print(f"\nStandard bracket for {selected['name']}: {selected['range_label']}")
    base_input = input(f"Enter Base Tier Price in INR [Default: ₹{selected['default_base']:,.0f}]: ").strip()
    if base_input:
        try:
            base_price = float(base_input)
        except ValueError:
            base_price = selected['default_base']
    else:
        base_price = selected['default_base']

    # Custom Feature Increments Checkpoint
    print("\n" + "-"*65)
    print("⚡ FEATURE INCREMENTS & CUSTOM ADD-ONS CHECKPOINT")
    print("-" * 65)
    has_custom = input("Did the client request feature increments beyond standard scope? (y/n): ").strip().lower()

    custom_features_desc = "None"
    custom_surcharge = 0.0

    if has_custom == 'y':
        custom_features_desc = input("Describe the extra features requested (e.g. Gateway, AI Chatbot, Portal): ").strip()
        print(f"\nBase {selected['name']} Price: ₹{base_price:,.2f} INR")
        while True:
            add_price = input(f"How much ADDITIONAL price (INR) should we add for '{custom_features_desc}'?: ").strip()
            try:
                custom_surcharge = float(add_price)
                if custom_surcharge < 0:
                    print("Price cannot be negative.")
                    continue
                break
            except ValueError:
                print("Please enter a valid numeric amount.")

    total_price = base_price + custom_surcharge
    scope_desc = f"{selected['name']} Tier ({selected['summary']})"
    if custom_surcharge > 0:
        scope_desc += f" + Feature Increments: {custom_features_desc}"

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO deals (lead_id, tier_selected, base_price_inr, custom_features, custom_surcharge_inr, proposed_price_inr, project_scope, quote_approved_by_owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    ''', (lead_id, selected['name'], base_price, custom_features_desc, custom_surcharge, total_price, scope_desc))
    deal_id = cur.lastrowid
    conn.commit()
    conn.close()

    print(f"\n[OK] Deal #{deal_id} created successfully!")
    print(f"Base Tier Price:     ₹{base_price:,.2f} INR")
    if custom_surcharge > 0:
        print(f"Feature Increments:  +₹{custom_surcharge:,.2f} INR (For: {custom_features_desc})")
    print(f"Final Agreed Amount: ₹{total_price:,.2f} INR")
    print("[GATE 1 ACTIVE] Quote is locked pending your human approval.")

def gate_1_approve_quote():
    print("\n--- [GATE 1] REVIEW & APPROVE TIER QUOTATION ---")
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.tier_selected, d.base_price_inr, d.custom_features, d.custom_surcharge_inr, d.proposed_price_inr, d.project_scope 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.quote_approved_by_owner = 0
    ''')
    pending = cur.fetchall()

    if not pending:
        print("No quotations waiting for owner approval.")
        conn.close()
        return

    for q in pending:
        print(f"\nDeal #{q['id']} for '{q['business_name']}'")
        print(f"Tier:            {q['tier_selected']} (Base: ₹{q['base_price_inr']:,.2f})")
        if q['custom_surcharge_inr'] > 0:
            print(f"Increments:      {q['custom_features']} (+₹{q['custom_surcharge_inr']:,.2f})")
        print(f"Total Amount:    ₹{q['proposed_price_inr']:,.2f} INR")
        print(f"Scope:           {q['project_scope']}")
        choice = input("Authorize sending this quotation & price to client? (y/n): ").strip().lower()
        if choice == 'y':
            cur.execute("UPDATE deals SET quote_approved_by_owner = 1 WHERE id = ?", (q['id'],))
            conn.commit()
            print(f"[APPROVED] Deal #{q['id']} authorized. Ready for client invoice.")
    conn.close()

def generate_invoice():
    print("\n--- [PAYMENT REQUEST] INVOICE GENERATOR ---")
    deal_id = input("Enter Approved Deal ID: ").strip()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.tier_selected, d.base_price_inr, d.custom_features, d.custom_surcharge_inr, d.proposed_price_inr, d.project_scope, d.quote_approved_by_owner 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.id = ?
    ''', (deal_id,))
    deal = cur.fetchone()
    conn.close()

    if not deal:
        print("[!] Deal not found.")
        return
    if not deal['quote_approved_by_owner']:
        print("[!] Error: Gate 1 approval required before generating invoice.")
        return

    cfg = get_config()
    upi_id = cfg.get("GPAY_UPI_ID")
    payee = cfg.get("GPAY_PAYEE_NAME")
    beneficiary = cfg.get("GPAY_BENEFICIARY_NAME")
    email = cfg.get("AGENCY_CONTACT_EMAIL")
    amount = deal['proposed_price_inr']

    encoded_name = urllib.parse.quote(payee)
    encoded_note = urllib.parse.quote(f"WI-{deal['id']:04d}")
    upi_link = f"upi://pay?pa={upi_id}&pn={encoded_name}&am={amount:.2f}&cu=INR&tn={encoded_note}"

    print("\n" + "="*65)
    print("                 WHITE INTENTION - OFFICIAL INVOICE")
    print("="*65)
    print(f"Client:              {deal['business_name']}")
    print(f"Invoice Ref:         WI-{deal['id']:04d}")
    print(f"Package:             {deal['tier_selected']} (Base: ₹{deal['base_price_inr']:,.2f})")
    if deal['custom_surcharge_inr'] > 0:
        print(f"Feature Increments:  {deal['custom_features']} (+₹{deal['custom_surcharge_inr']:,.2f})")
    print(f"Total Amount Due:    ₹{amount:,.2f} INR")
    print(f"Billing Email:       {email}")
    print("-"*65)
    print("VERIFIED UPI PAYMENT INSTRUCTIONS:")
    print(f"1. UPI / Google Pay ID:  {upi_id}")
    print(f"2. Organization:         {payee}")
    print(f"3. Bank Beneficiary:     {beneficiary} (Authorized Lead)")
    print(f"4. Direct Tap Link:      {upi_link}")
    print("-"*65)
    print("Client Payment Notice:")
    print(f"When paying on Google Pay/PhonePe/Paytm, the bank screen will confirm")
    print(f"the authorized beneficiary: '{beneficiary}'.")
    print("Please reply with your UTR / transaction ref to initiate deployment.")
    print("="*65)

def gate_2_verify_and_build():
    print("\n--- [GATE 2] MANUAL PAYMENT VERIFICATION & MARKET BUILD ---")
    print("Rule: Never trust customer screenshots. Verify direct bank credit.")
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, l.industry, d.tier_selected, d.custom_features, d.proposed_price_inr, d.project_scope 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.quote_approved_by_owner = 1 AND d.payment_verified_by_owner = 0
    ''')
    deals = cur.fetchall()

    if not deals:
        print("No deals currently waiting for payment verification.")
        conn.close()
        return

    for d in deals:
        print(f"\nDeal #{d['id']} for '{d['business_name']}' - Tier: {d['tier_selected']} - Expected: ₹{d['proposed_price_inr']:,.2f}")
        confirm = input("Have you verified this exact amount in your GPay/Bank? (y/n): ").strip().lower()
        if confirm == 'y':
            tier = d['tier_selected']
            b_name = d['business_name']
            ind = d['industry'] or "Professional Services"
            custom_badge = f"<span class='text-xs bg-purple-500/20 text-purple-300 border border-purple-500/40 px-3 py-1 rounded-full'>Includes: {d['custom_features']}</span>" if d['custom_features'] != "None" else ""

            badge_color = "bg-blue-600" if "Basic" in tier else ("bg-emerald-600" if "Average" in tier else "bg-purple-600")
            
            html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{b_name} | Premium {ind} Solutions</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 font-sans antialiased selection:bg-blue-500 selection:text-white">

    <div class="bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-700 py-2.5 px-4 text-center text-xs font-semibold tracking-wide uppercase">
        🚀 Official Modernized Experience • Verified & Engineered by White Intention
    </div>

    <header class="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl {badge_color} flex items-center justify-center font-bold text-white shadow-lg">
                    {b_name[:2].upper()}
                </div>
                <span class="text-2xl font-black tracking-tight text-white">{b_name}</span>
            </div>
            <nav class="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
                <a href="#about" class="hover:text-white transition">About</a>
                <a href="#services" class="hover:text-white transition">Services</a>
                <a href="#contact" class="px-5 py-2.5 rounded-xl {badge_color} text-white font-bold hover:opacity-90 shadow-lg transition">Get In Touch</a>
            </nav>
        </div>
    </header>

    <section class="relative pt-24 pb-20 px-6 overflow-hidden">
        <div class="max-w-5xl mx-auto text-center">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-blue-400 text-xs font-bold uppercase tracking-widest mb-8">
                <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                Leading {ind} Expertise
            </div>
            <h1 class="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-tight mb-8">
                Elevating Excellence in <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">{ind}</span>
            </h1>
            <p class="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                Dedicated to delivering premier standards, transparent processes, and tailored outcomes designed around your peace of mind.
            </p>
            <div class="flex flex-col sm:flex-row justify-center gap-4">
                <a href="#contact" class="px-8 py-4 rounded-xl {badge_color} text-white font-bold text-base shadow-xl hover:opacity-90 transition">
                    Book Consultation Now
                </a>
                <a href="https://wa.me/919999999999" target="_blank" class="px-8 py-4 rounded-xl bg-emerald-600/20 border border-emerald-500/40 text-emerald-400 font-bold text-base hover:bg-emerald-600/30 transition flex items-center justify-center gap-2">
                    <i class="fab fa-whatsapp"></i> Chat on WhatsApp
                </a>
            </div>
        </div>
    </section>

    <!-- Scope Box -->
    <section class="max-w-6xl mx-auto px-6 py-8">
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-3xl p-8 shadow-2xl">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-slate-700">
                <div>
                    <span class="text-xs uppercase tracking-wider text-slate-400 font-bold">Package Delivered</span>
                    <h3 class="text-2xl font-bold text-white flex items-center gap-3">
                        {tier} Architecture {custom_badge}
                    </h3>
                </div>
                <div class="text-right">
                    <span class="text-xs uppercase tracking-wider text-slate-400 font-bold">Investment Verified</span>
                    <p class="text-2xl font-black text-emerald-400">₹{d['proposed_price_inr']:,.2f} INR</p>
                </div>
            </div>
            <div class="mt-6 text-sm text-slate-300 space-y-2">
                <p class="font-semibold text-slate-200">System Specifications & Scope:</p>
                <p class="text-slate-400">{d['project_scope']}</p>
            </div>
        </div>
    </section>

    <section id="services" class="max-w-7xl mx-auto px-6 py-20">
        <div class="text-center max-w-2xl mx-auto mb-16">
            <h2 class="text-3xl md:text-4xl font-extrabold text-white mb-4">Engineered For Reliable Results</h2>
            <p class="text-slate-400">Every aspect of our practice is optimized for clarity, speed, and premium quality.</p>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-slate-800/60 border border-slate-700/80 p-8 rounded-2xl hover:border-blue-500/50 transition">
                <div class="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-xl mb-6">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Certified Trust</h3>
                <p class="text-slate-400 text-sm leading-relaxed">Rigorous adherence to premier benchmarks, ensuring every client engagement receives uncompromised standards.</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/80 p-8 rounded-2xl hover:border-emerald-500/50 transition">
                <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl mb-6">
                    <i class="fas fa-bolt"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Rapid Turnaround</h3>
                <p class="text-slate-400 text-sm leading-relaxed">Streamlined digital communication and swift case management to save your time and eliminate unnecessary delays.</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/80 p-8 rounded-2xl hover:border-purple-500/50 transition">
                <div class="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center text-xl mb-6">
                    <i class="fas fa-user-check"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Tailored Solutions</h3>
                <p class="text-slate-400 text-sm leading-relaxed">No generic templates. Every consultation is precisely adapted to your personal or commercial requirements.</p>
            </div>
        </div>
    </section>

    <a href="https://wa.me/919999999999" target="_blank" class="fixed bottom-8 right-8 z-50 bg-emerald-500 text-white w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-2xl hover:scale-110 transition duration-300">
        <i class="fab fa-whatsapp"></i>
    </a>

    <footer class="border-t border-slate-800 py-12 text-center text-xs text-slate-500">
        <p class="mb-2">&copy; {b_name}. All rights reserved.</p>
        <p>Architected, Modernized & Deployed by <span class="text-slate-300 font-semibold">White Intention Agency</span></p>
    </footer>

</body>
</html>"""
            preview_file = PREVIEWS_DIR / f"preview_deal_{d['id']}.html"
            with open(preview_file, "w", encoding="utf-8") as pf:
                pf.write(html)

            cur.execute('''
                UPDATE deals 
                SET payment_status = "paid", payment_verified_by_owner = 1, preview_url = ? 
                WHERE id = ?
            ''', (str(preview_file.resolve()), d['id']))
            conn.commit()

            print(f"[VERIFIED] Deal #{d['id']} marked PAID.")
            print(f"[MARKET BUILDER] Generated {tier} website draft: {preview_file}")
    conn.close()

def gate_3_review_delivery():
    print("\n--- [GATE 3] FINAL DELIVERY & HANDOVER SIGN-OFF ---")
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.tier_selected, d.preview_url 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.payment_verified_by_owner = 1 AND d.delivery_approved_by_owner = 0
    ''')
    deals = cur.fetchall()

    if not deals:
        print("No completed builds waiting for final delivery approval.")
        conn.close()
        return

    for d in deals:
        print(f"\nDeal #{d['id']} for '{d['business_name']}' - Tier: {d['tier_selected']}")
        preview = d['preview_url']
        print(f"Preview Location: {preview}")
        
        view = input("Launch website in your browser to inspect design? (y/n): ").strip().lower()
        if view == 'y' and preview and os.path.exists(preview):
            os.system(f'start "" "{preview}"')

        release = input("Authorize sending final website & source code to client? (y/n): ").strip().lower()
        if release == 'y':
            cur.execute('''
                UPDATE deals 
                SET delivery_status = "delivered", delivery_approved_by_owner = 1 
                WHERE id = ?
            ''', (d['id'],))
            conn.commit()
            print(f"[DELIVERED] Deal #{d['id']} approved. Handover completed!")
    conn.close()

def list_leads():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    print("\n" + "="*75)
    print("WHITE INTENTION - LEADS & REQUIREMENT DIRECTORY")
    print("="*75)
    if not rows:
        print("No leads recorded yet.")
        return
    for r in rows:
        print(f"Lead #{r['id']} | {r['business_name']} ({r['industry']}) | Rec. Tier: {r['recommended_tier']}")
        print(f"Contact: {r['contact_channel']} ({r['contact_value']}) | Status: {r['status']}")
        print(f"Stated Needs: {r['raw_requirements']}")
        print("-" * 75)

# ----------------- MAIN CLI -----------------
def main():
    init_db()
    while True:
        print("\n" + "="*62)
        print("      WHITE INTENTION - 200-IQ AGENCY CONSOLE")
        print("="*62)
        print("1. Ingest Lead, Analyze Requirements & Get Tier Recommendation")
        print("2. List All Leads & Requirement Diagnostics")
        print("3. Draft Tiered Quotation (Basic: 20-30k / Average: 35-40k / Advance: 45-60k+)")
        print("4. [GATE 1] Review & Approve Proposal & Pricing")
        print("5. Generate Verified Client UPI Invoice")
        print("6. [GATE 2] Verify Bank Payment & Auto-Build Market Website")
        print("7. [GATE 3] Inspect Website Preview & Authorize Delivery")
        print("8. Exit")
        print("="*62)
        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            add_and_analyze_lead()
        elif choice == "2":
            list_leads()
        elif choice == "3":
            draft_tiered_quote()
        elif choice == "4":
            gate_1_approve_quote()
        elif choice == "5":
            generate_invoice()
        elif choice == "6":
            gate_2_verify_and_build()
        elif choice == "7":
            gate_3_review_delivery()
        elif choice == "8":
            print("\nExiting White Intention console.")
            sys.exit(0)
        else:
            print("Invalid option. Enter 1-8.")

if __name__ == "__main__":
    main()
