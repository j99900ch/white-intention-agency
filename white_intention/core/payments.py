import urllib.parse
from pathlib import Path
from white_intention.core.db import get_connection

ENV_PATH = Path("./white_intention/.env")

def load_payment_config():
    if not ENV_PATH.exists():
        return {}
    config = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip().strip('"').strip("'")
    return config

def generate_upi_link(amount: float, note: str = "White Intention Web Services"):
    cfg = load_payment_config()
    upi_id = cfg.get("GPAY_UPI_ID", "")
    payee_name = cfg.get("GPAY_PAYEE_NAME", "White Intention")
    
    if not upi_id:
        return None, "Error: GPAY_UPI_ID is not configured in .env"

    encoded_name = urllib.parse.quote(payee_name)
    encoded_note = urllib.parse.quote(note)
    
    # Direct UPI Intent link (opens GPay / PhonePe / Paytm directly on mobile)
    upi_uri = f"upi://pay?pa={upi_id}&pn={encoded_name}&am={amount:.2f}&cu=INR&tn={encoded_note}"
    return upi_uri, None

def format_payment_instructions(deal_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.project_scope, d.proposed_price_inr 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.id = ?
    ''', (deal_id,))
    deal = cur.fetchone()
    conn.close()

    if not deal:
        return "Deal not found."

    cfg = load_payment_config()
    upi_id = cfg.get("GPAY_UPI_ID", "Not configured")
    payee_name = cfg.get("GPAY_PAYEE_NAME", "White Intention")
    beneficiary_name = cfg.get("GPAY_BENEFICIARY_NAME", "Jyoti Chaudhary")
    contact_email = cfg.get("AGENCY_CONTACT_EMAIL", "chaudharyjyoti0754@gmail.com")
    amount = deal["proposed_price_inr"]

    upi_link, _ = generate_upi_link(amount, f"Invoice WI-{deal['id']:04d}")

    invoice = f"""
=============================================================
             WHITE INTENTION - PAYMENT REQUEST
=============================================================
Client:               {deal['business_name']}
Invoice Ref:          WI-{deal['id']:04d}
Scope:                {deal['project_scope']}
Total Payable:        ₹{amount:,.2f} INR
Billing Contact:      {contact_email}

--- PAYMENT INSTRUCTIONS (UPI / GPAY) ---
1. Pay via UPI ID / VPA:
   UPI ID:            {upi_id}
   Agency:            {payee_name}
   Account Name:      {beneficiary_name} (Authorized Lead)

2. Instant Mobile Tap-to-Pay:
   {upi_link}

* Important Note:
  When transferring via Google Pay, PhonePe, or Paytm, the recipient 
  display will confirm the authorized account name '{beneficiary_name}'.
  
  Once paid, reply with your Transaction Reference / UTR number 
  so we can verify and initiate project delivery immediately.
=============================================================
"""
    return invoice

if __name__ == "__main__":
    print(format_payment_instructions(1))
