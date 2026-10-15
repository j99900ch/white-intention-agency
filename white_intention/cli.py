import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from white_intention.core.db import init_db, get_connection
from white_intention.agents.outreach import OutreachAgent
from white_intention.core.payments import format_payment_instructions
from white_intention.agents.builder import WebsiteBuilderAgent

def show_menu():
    print("\n" + "="*55)
    print("      WHITE INTENTION - AGENCY CONTROL CONSOLE")
    print("="*55)
    print("1. Add a Discovered Lead")
    print("2. List Leads & Outreach Status")
    print("3. Create Draft Quotation for Client")
    print("4. [GATE 1] Review & Approve Quotations / Pricing")
    print("5. Generate & Send GPay / UPI Invoice")
    print("6. [GATE 2] Verify Received UPI Payment & Build Preview")
    print("7. [GATE 3] Review Preview & Approve Delivery")
    print("8. Exit")
    print("="*55)

def add_lead_interactive():
    name = input("Business Name: ").strip()
    site = input("Website / Profile URL: ").strip()
    channel = input("Contact Channel (Email/Insta/LinkedIn): ").strip()
    contact = input("Email / Handle / Phone: ").strip()
    issue = input("Need Identified (e.g. outdated design, no mobile support): ").strip()
    
    lead_id, msg = OutreachAgent.add_lead(name, site, channel, contact, issue)
    if lead_id:
        print(f"\n[OK] Lead registered with ID #{lead_id}")
        draft = OutreachAgent.generate_soft_intro(name, issue)
        print("\n--- Generated Soft Outreach Message ---")
        print(draft)
    else:
        print(f"[!] {msg}")

def list_leads():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, business_name, website_url, contact_channel, status FROM leads")
    rows = cur.fetchall()
    print("\nID | Business Name | Channel | Status | Website")
    print("-" * 65)
    for r in rows:
        print(f"{r['id']} | {r['business_name']} | {r['contact_channel']} | {r['status']} | {r['website_url']}")
    conn.close()

def create_quote():
    lead_id = input("Enter Lead ID: ").strip()
    scope = input("Project Scope (e.g., 5-page responsive site + SEO): ").strip()
    price = float(input("Proposed Price (INR): ").strip())
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO deals (lead_id, project_scope, proposed_price_inr, quote_approved_by_owner)
        VALUES (?, ?, ?, 0)
    ''', (lead_id, scope, price))
    conn.commit()
    conn.close()
    print(f"\n[OK] Quotation drafted for Rs {price:,.2f}. Status: PENDING OWNER APPROVAL.")

def approve_quotes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.project_scope, d.proposed_price_inr 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.quote_approved_by_owner = 0
    ''')
    pending = cur.fetchall()
    if not pending:
        print("\nNo quotations waiting for approval.")
        conn.close()
        return

    print("\n--- Quotations Pending Your Approval ---")
    for q in pending:
        print(f"\nDeal #{q['id']} for '{q['business_name']}'")
        print(f"Scope:  {q['project_scope']}")
        print(f"Amount: Rs {q['proposed_price_inr']:,.2f}")
        choice = input("Approve sending this quote? (y/n): ").strip().lower()
        if choice == 'y':
            cur.execute("UPDATE deals SET quote_approved_by_owner = 1 WHERE id = ?", (q['id'],))
            conn.commit()
            print(f"[APPROVED] Deal #{q['id']} approved. Ready to generate invoice.")
    conn.close()

def show_invoice():
    deal_id = input("Enter Approved Deal ID: ").strip()
    invoice_text = format_payment_instructions(int(deal_id))
    print(invoice_text)

def verify_payment_and_build():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.proposed_price_inr 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.quote_approved_by_owner = 1 AND d.payment_verified_by_owner = 0
    ''')
    deals = cur.fetchall()
    if not deals:
        print("\nNo deals waiting for payment verification.")
        conn.close()
        return

    print("\n--- Manual Payment Verification Checkpoint ---")
    print("Rule: Never rely solely on customer screenshots. Confirm the credit in your banking/UPI app.")
    for d in deals:
        print(f"\nDeal #{d['id']} - {d['business_name']} - Expected Amount: Rs {d['proposed_price_inr']:,.2f}")
        choice = input("Have you verified this exact payment in your bank/GPay? (y/n): ").strip().lower()
        if choice == 'y':
            cur.execute('''
                UPDATE deals 
                SET payment_status = "paid", payment_verified_by_owner = 1 
                WHERE id = ?
            ''', (d['id'],))
            conn.commit()
            print(f"[CONFIRMED] Deal #{d['id']} marked as Paid.")
            
            print("[BUILDER AGENT] Generating website preview...")
            preview_file, msg = WebsiteBuilderAgent.build_landing_page(d['id'])
            print(f"[BUILDER AGENT] {msg}\nPreview saved at:\n{preview_file}")
    conn.close()

def approve_delivery():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT d.id, l.business_name, d.preview_url 
        FROM deals d JOIN leads l ON d.lead_id = l.id 
        WHERE d.payment_verified_by_owner = 1 AND d.delivery_approved_by_owner = 0
    ''')
    deals = cur.fetchall()
    if not deals:
        print("\nNo projects waiting for delivery sign-off.")
        conn.close()
        return

    print("\n--- Final Delivery Review Checkpoint ---")
    for d in deals:
        print(f"\nDeal #{d['id']} for '{d['business_name']}'")
        print(f"Preview File: {d['preview_url']}")
        choice = input("Open file in browser to review before sending? (y/n): ").strip().lower()
        if choice == 'y' and d['preview_url']:
            os.system(f'start "" "{d["preview_url"]}"')
        
        deliver = input("Authorize customer delivery / release? (y/n): ").strip().lower()
        if deliver == 'y':
            cur.execute('''
                UPDATE deals 
                SET delivery_status = "delivered", delivery_approved_by_owner = 1 
                WHERE id = ?
            ''', (d['id'],))
            conn.commit()
            print(f"[DELIVERED] Deal #{d['id']} marked delivered. Customer handover authorized.")
    conn.close()

def main():
    init_db()
    while True:
        show_menu()
        choice = input("Select an option (1-8): ").strip()
        if choice == "1":
            add_lead_interactive()
        elif choice == "2":
            list_leads()
        elif choice == "3":
            create_quote()
        elif choice == "4":
            approve_quotes()
        elif choice == "5":
            show_invoice()
        elif choice == "6":
            verify_payment_and_build()
        elif choice == "7":
            approve_delivery()
        elif choice == "8":
            print("Exiting White Intention Console.")
            sys.exit(0)
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()