import streamlit as st
import json
import pandas as pd
import hashlib
import os
from datetime import date, datetime

LEADS_FILE = "leads.json"
USERS_FILE = "users.json"

st.set_page_config(
    page_title="TrueNorth CRM",
    page_icon="🧭",
    layout="wide"
)

# ---------- BASIC DATABASE FUNCTIONS ----------

def load_json(file_name, default):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default

def save_json(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def money(value):
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except:
        return 0

def balance_due(lead):
    return money(lead.get("amount_owed", 0)) - money(lead.get("amount_paid", 0))

users = load_json(USERS_FILE, {})
all_leads = load_json(LEADS_FILE, {})

# ---------- SESSION STATE ----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- AUTH PAGE ----------

if not st.session_state.logged_in:
    st.title("🧭 TrueNorth CRM")
    st.caption("Simple CRM for realtors, cleaning companies, and local service businesses.")

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True):
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_signup:
        new_username = st.text_input("Create Username", key="signup_user")
        new_password = st.text_input("Create Password", type="password", key="signup_pass")
        business_name = st.text_input("Business Name", value="My Business CRM")
        business_type = st.selectbox("Business Type", ["Real Estate", "Cleaning", "Both", "Other"])

        if st.button("Create Account", use_container_width=True):
            if not new_username or not new_password:
                st.warning("Please enter a username and password.")
            elif new_username in users:
                st.warning("That username already exists.")
            else:
                users[new_username] = {
                    "password": hash_password(new_password),
                    "business_name": business_name,
                    "business_type": business_type,
                    "created_at": str(datetime.now())
                }

                all_leads[new_username] = []

                save_json(USERS_FILE, users)
                save_json(LEADS_FILE, all_leads)

                st.success("Account created! You can now log in.")

    st.stop()

# ---------- USER DATA ----------

username = st.session_state.username
user = users.get(username, {})
business_name = user.get("business_name", "TrueNorth CRM")

if username not in all_leads:
    all_leads[username] = []

leads = all_leads[username]

# ---------- SIDEBAR ----------

with st.sidebar:
    st.title("🧭 TrueNorth CRM")
    st.write(f"**Business:** {business_name}")
    st.write(f"**User:** {username}")

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ---------- HEADER ----------

st.title(f"{business_name} 💼")
st.caption("Lead Tracking • Follow-Ups • Payments • Pipeline Management")

tabs = st.tabs([
    "📊 Dashboard",
    "➕ Add Lead",
    "📋 Leads",
    "💰 Payments",
    "📅 Follow-Ups",
    "📤 Export",
    "⚙️ Settings"
])

# ---------- DASHBOARD ----------

with tabs[0]:
    total_leads = len(leads)
    closed_leads = len([lead for lead in leads if lead.get("status") == "Closed"])
    today_followups = len([lead for lead in leads if lead.get("follow_up") == str(date.today())])
    pipeline_value = sum(money(lead.get("quote", 0)) for lead in leads)
    total_paid = sum(money(lead.get("amount_paid", 0)) for lead in leads)
    total_owed = sum(money(lead.get("amount_owed", 0)) for lead in leads)
    total_balance = total_owed - total_paid
    commission_total = sum(money(lead.get("commission_estimate", 0)) for lead in leads)

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    col1.metric("Total Leads", total_leads)
    col2.metric("Closed", closed_leads)
    col3.metric("Follow-Ups Today", today_followups)
    col4.metric("Pipeline", f"${pipeline_value:,.0f}")
    col5.metric("Paid", f"${total_paid:,.0f}")
    col6.metric("Balance Due", f"${total_balance:,.0f}")
    col7.metric("Commission Est.", f"${commission_total:,.0f}")

    st.divider()

    st.subheader("🔥 Today’s Follow-Ups")

    due_today = [lead for lead in leads if lead.get("follow_up") == str(date.today())]

    if due_today:
        for lead in due_today:
            with st.container(border=True):
                st.write(f"### {lead.get('name', 'No Name')}")
                st.write(f"📞 **Phone:** {lead.get('phone', '')}")
                st.write(f"📧 **Email:** {lead.get('email', '')}")
                st.write(f"📍 **Address:** {lead.get('address', '')}")
                st.write(f"👉 **Next Action:** {lead.get('next_action', '')}")
                st.write(f"📝 **Notes:** {lead.get('notes', '')}")
    else:
        st.success("No follow-ups due today.")

# ---------- ADD LEAD ----------

with tabs[1]:
    st.subheader("➕ Add New Lead")

    colA, colB = st.columns(2)

    with colA:
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_input("Address")
        lead_source = st.selectbox("Lead Source", ["Facebook", "Instagram", "Zillow", "Referral", "Sign Call", "Website", "Past Client", "Other"])
        service = st.selectbox("Lead Type", ["Buyer Lead", "Seller Lead", "Cleaning Client", "Referral", "Other"])
        status = st.selectbox("Status", ["New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"])

    with colB:
        follow_up = st.date_input("Follow-Up Date", value=date.today())
        last_contacted = st.date_input("Last Contacted Date", value=date.today())
        quote = st.text_input("Deal Value / Cleaning Quote ($)")
        amount_owed = st.text_input("Amount Owed ($)")
        amount_paid = st.text_input("Amount Paid ($)")
        deposit_paid = st.text_input("Deposit Paid ($)")
        payment_status = st.selectbox("Payment Status", ["Unpaid", "Partial", "Paid"])
        invoice_status = st.selectbox("Invoice Status", ["Not Sent", "Sent", "Paid", "Overdue"])

    st.subheader("🏠 Property / Job Details")

    colC, colD, colE = st.columns(3)

    with colC:
        bedrooms = st.text_input("Bedrooms")
        bathrooms = st.text_input("Bathrooms")
        square_feet = st.text_input("Square Feet")

    with colD:
        property_type = st.selectbox("Property Type", ["House", "Condo", "Townhome", "Mobile Home", "Commercial", "Other"])
        cleaning_frequency = st.selectbox("Cleaning Frequency", ["One-Time", "Weekly", "Biweekly", "Monthly", "As Needed", "N/A"])

    with colE:
        buyer_budget = st.text_input("Buyer Budget ($)")
        seller_timeline = st.text_input("Seller Timeline")
        commission_estimate = st.text_input("Commission Estimate ($)")

    next_action = st.text_input("Next Action")
    notes = st.text_area("Notes")
    call_log_entry = st.text_area("Add First Call / Task Note")

    if st.button("Save Lead", use_container_width=True):
        if name and phone:
            new_lead = {
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
                "lead_source": lead_source,
                "service": service,
                "status": status,
                "follow_up": str(follow_up),
                "last_contacted": str(last_contacted),
                "quote": quote,
                "amount_owed": amount_owed,
                "amount_paid": amount_paid,
                "deposit_paid": deposit_paid,
                "payment_status": payment_status,
                "invoice_status": invoice_status,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "square_feet": square_feet,
                "property_type": property_type,
                "cleaning_frequency": cleaning_frequency,
                "buyer_budget": buyer_budget,
                "seller_timeline": seller_timeline,
                "commission_estimate": commission_estimate,
                "next_action": next_action,
                "notes": notes,
                "call_log": []
            }

            if call_log_entry:
                new_lead["call_log"].append({
                    "date": str(datetime.now()),
                    "note": call_log_entry
                })

            leads.append(new_lead)
            all_leads[username] = leads
            save_json(LEADS_FILE, all_leads)

            st.success("Lead saved!")
            st.rerun()
        else:
            st.warning("Please enter a name and phone number.")

# ---------- LEADS ----------

with tabs[2]:
    st.subheader("📋 Leads")

    search = st.text_input("Search by name, phone, email, or address")
    status_filter = st.selectbox("Filter by status", ["All", "New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"])
    source_filter = st.selectbox("Filter by lead source", ["All", "Facebook", "Instagram", "Zillow", "Referral", "Sign Call", "Website", "Past Client", "Other"])

    filtered_leads = []

    for lead in leads:
        matches_search = (
            search.lower() in lead.get("name", "").lower()
            or search.lower() in lead.get("phone", "").lower()
            or search.lower() in lead.get("email", "").lower()
            or search.lower() in lead.get("address", "").lower()
        )

        matches_status = status_filter == "All" or lead.get("status", "New") == status_filter
        matches_source = source_filter == "All" or lead.get("lead_source", "Other") == source_filter

        if matches_search and matches_status and matches_source:
            filtered_leads.append(lead)

    if filtered_leads:
        for index, lead in enumerate(filtered_leads):
            real_index = leads.index(lead)

            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                col1.subheader(lead.get("name", "No Name"))
                col2.write(f"**Status:** {lead.get('status', 'New')}")
                col3.write(f"**Balance:** ${balance_due(lead):,.0f}")

                if lead.get("follow_up") == str(date.today()):
                    st.error("⚠️ FOLLOW UP TODAY")

                st.write(f"📞 **Phone:** {lead.get('phone', '')}")
                st.write(f"📧 **Email:** {lead.get('email', '')}")
                st.write(f"📍 **Address:** {lead.get('address', '')}")
                st.write(f"📣 **Source:** {lead.get('lead_source', '')}")
                st.write(f"🏷️ **Type:** {lead.get('service', '')}")
                st.write(f"📅 **Follow-Up:** {lead.get('follow_up', '')}")
                st.write(f"🕒 **Last Contacted:** {lead.get('last_contacted', '')}")
                st.write(f"👉 **Next Action:** {lead.get('next_action', '')}")
                st.write(f"📝 **Notes:** {lead.get('notes', '')}")

                with st.expander("✏️ Edit Lead"):
                    statuses = ["New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"]
                    payment_statuses = ["Unpaid", "Partial", "Paid"]
                    invoice_statuses = ["Not Sent", "Sent", "Paid", "Overdue"]

                    edit_status = st.selectbox("Status", statuses, index=statuses.index(lead.get("status", "New")), key=f"status-{real_index}")
                    edit_follow_up = st.date_input("Follow-Up Date", value=date.fromisoformat(lead.get("follow_up", str(date.today()))), key=f"follow-{real_index}")
                    edit_last_contacted = st.date_input("Last Contacted", value=date.fromisoformat(lead.get("last_contacted", str(date.today()))), key=f"last-{real_index}")
                    edit_amount_owed = st.text_input("Amount Owed", value=lead.get("amount_owed", ""), key=f"owed-{real_index}")
                    edit_amount_paid = st.text_input("Amount Paid", value=lead.get("amount_paid", ""), key=f"paid-{real_index}")
                    edit_deposit_paid = st.text_input("Deposit Paid", value=lead.get("deposit_paid", ""), key=f"deposit-{real_index}")
                    edit_payment_status = st.selectbox("Payment Status", payment_statuses, index=payment_statuses.index(lead.get("payment_status", "Unpaid")), key=f"paystatus-{real_index}")
                    edit_invoice_status = st.selectbox("Invoice Status", invoice_statuses, index=invoice_statuses.index(lead.get("invoice_status", "Not Sent")), key=f"invoice-{real_index}")
                    edit_next_action = st.text_input("Next Action", value=lead.get("next_action", ""), key=f"action-{real_index}")
                    edit_notes = st.text_area("Notes", value=lead.get("notes", ""), key=f"notes-{real_index}")
                    new_log = st.text_area("Add Call / Task Note", key=f"log-{real_index}")

                    if st.button("Save Updates", key=f"save-{real_index}"):
                        leads[real_index]["status"] = edit_status
                        leads[real_index]["follow_up"] = str(edit_follow_up)
                        leads[real_index]["last_contacted"] = str(edit_last_contacted)
                        leads[real_index]["amount_owed"] = edit_amount_owed
                        leads[real_index]["amount_paid"] = edit_amount_paid
                        leads[real_index]["deposit_paid"] = edit_deposit_paid
                        leads[real_index]["payment_status"] = edit_payment_status
                        leads[real_index]["invoice_status"] = edit_invoice_status
                        leads[real_index]["next_action"] = edit_next_action
                        leads[real_index]["notes"] = edit_notes

                        if new_log:
                            if "call_log" not in leads[real_index]:
                                leads[real_index]["call_log"] = []

                            leads[real_index]["call_log"].append({
                                "date": str(datetime.now()),
                                "note": new_log
                            })

                        all_leads[username] = leads
                        save_json(LEADS_FILE, all_leads)
                        st.success("Lead updated!")
                        st.rerun()

                with st.expander("📞 Call / Task Log"):
                    logs = lead.get("call_log", [])

                    if logs:
                        for log in logs:
                            st.write(f"**{log.get('date', '')}**")
                            st.write(log.get("note", ""))
                            st.divider()
                    else:
                        st.write("No call notes yet.")

                if st.button("Delete Lead", key=f"delete-{real_index}"):
                    leads.pop(real_index)
                    all_leads[username] = leads
                    save_json(LEADS_FILE, all_leads)
                    st.rerun()
    else:
        st.info("No leads found.")

# ---------- PAYMENTS ----------

with tabs[3]:
    st.subheader("💰 Payments")

    unpaid = [lead for lead in leads if balance_due(lead) > 0]

    if unpaid:
        for lead in unpaid:
            with st.container(border=True):
                st.write(f"### {lead.get('name', 'No Name')}")
                st.write(f"📞 **Phone:** {lead.get('phone', '')}")
                st.write(f"💸 **Owed:** ${money(lead.get('amount_owed', 0)):,.0f}")
                st.write(f"✅ **Paid:** ${money(lead.get('amount_paid', 0)):,.0f}")
                st.write(f"💵 **Deposit:** ${money(lead.get('deposit_paid', 0)):,.0f}")
                st.write(f"📌 **Balance Due:** ${balance_due(lead):,.0f}")
                st.write(f"🧾 **Invoice:** {lead.get('invoice_status', 'Not Sent')}")
    else:
        st.success("No outstanding balances.")

# ---------- FOLLOW UPS ----------

with tabs[4]:
    st.subheader("📅 Follow-Ups")

    followups = [lead for lead in leads if lead.get("follow_up")]
    followups = sorted(followups, key=lambda lead: lead.get("follow_up", ""))

    if followups:
        for lead in followups:
            with st.container(border=True):
                if lead.get("follow_up") == str(date.today()):
                    st.error("⚠️ DUE TODAY")

                st.write(f"### {lead.get('name', 'No Name')}")
                st.write(f"📅 **Follow-Up:** {lead.get('follow_up', '')}")
                st.write(f"📞 **Phone:** {lead.get('phone', '')}")
                st.write(f"📧 **Email:** {lead.get('email', '')}")
                st.write(f"👉 **Next Action:** {lead.get('next_action', '')}")
                st.write(f"🕒 **Last Contacted:** {lead.get('last_contacted', '')}")
    else:
        st.info("No follow-ups scheduled.")

# ---------- EXPORT ----------

with tabs[5]:
    st.subheader("📤 Export Leads")

    if leads:
        df = pd.DataFrame(leads)
        csv = df.to_csv(index=False)

        st.download_button(
            label="Download Leads as CSV",
            data=csv,
            file_name=f"{business_name.replace(' ', '_').lower()}_leads.csv",
            mime="text/csv"
        )

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No leads to export yet.")

# ---------- SETTINGS ----------

with tabs[6]:
    st.subheader("⚙️ Account & Branding Settings")

    new_business_name = st.text_input("Business Name", value=business_name)
    new_business_type = st.selectbox(
        "Business Type",
        ["Real Estate", "Cleaning", "Both", "Other"],
        index=["Real Estate", "Cleaning", "Both", "Other"].index(user.get("business_type", "Both"))
    )

    if st.button("Save Branding Settings", use_container_width=True):
        users[username]["business_name"] = new_business_name
        users[username]["business_type"] = new_business_type
        save_json(USERS_FILE, users)
        st.success("Branding updated!")
        st.rerun()

    st.divider()

    st.warning("Prototype note: this login system is good for testing, but a real SaaS should use Supabase/Auth0/Firebase authentication and a real cloud database before selling to customers.")
