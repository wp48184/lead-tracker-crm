import streamlit as st
import json
from datetime import date

FILE_NAME = "leads.json"

st.set_page_config(page_title="William Locht CRM", page_icon="💼", layout="wide")

def load_leads():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_leads(leads):
    with open(FILE_NAME, "w") as file:
        json.dump(leads, file, indent=4)

def money(value):
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except:
        return 0

leads = load_leads()

st.title("William Locht CRM 💼")
st.caption("Ocala Real Estate + Cleaning Lead & Payment Tracker")

st.divider()

total_leads = len(leads)
closed_leads = len([lead for lead in leads if lead.get("status") == "Closed"])
today_followups = len([lead for lead in leads if lead.get("follow_up") == str(date.today())])
pipeline_value = sum(money(lead.get("quote", 0)) for lead in leads)
total_owed = sum(money(lead.get("amount_owed", 0)) for lead in leads)
total_paid = sum(money(lead.get("amount_paid", 0)) for lead in leads)
balance_due = total_owed - total_paid

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Leads", total_leads)
col2.metric("Closed Leads", closed_leads)
col3.metric("Follow-Ups Today", today_followups)
col4.metric("Pipeline Value", f"${pipeline_value:,.0f}")
col5.metric("Paid", f"${total_paid:,.0f}")
col6.metric("Balance Due", f"${balance_due:,.0f}")

st.divider()

left, right = st.columns([1, 2])

with left:
    st.subheader("➕ Add New Lead")

    name = st.text_input("Name")
    phone = st.text_input("Phone")
    address = st.text_input("Address")
    service = st.selectbox("Lead Type", ["Buyer Lead", "Seller Lead", "Cleaning Client", "Referral", "Other"])
    status = st.selectbox("Status", ["New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"])
    follow_up = st.date_input("Follow-Up Date", value=date.today())

    quote = st.text_input("Deal Value / Cleaning Quote ($)")
    amount_owed = st.text_input("Amount Owed ($)")
    amount_paid = st.text_input("Amount Paid ($)")
    payment_status = st.selectbox("Payment Status", ["Unpaid", "Partial", "Paid"])

    next_action = st.text_input("Next Action")
    notes = st.text_area("Notes")

    if st.button("Save Lead", use_container_width=True):
        if name and phone:
            new_lead = {
                "name": name,
                "phone": phone,
                "address": address,
                "service": service,
                "status": status,
                "follow_up": str(follow_up),
                "quote": quote,
                "amount_owed": amount_owed,
                "amount_paid": amount_paid,
                "payment_status": payment_status,
                "next_action": next_action,
                "notes": notes
            }

            leads.append(new_lead)
            save_leads(leads)
            st.success("Lead saved!")
            st.rerun()
        else:
            st.warning("Please enter a name and phone number.")

with right:
    st.subheader("📋 Lead Pipeline")

    search = st.text_input("Search by name, phone, or address")
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"]
    )

    payment_filter = st.selectbox(
        "Filter by payment status",
        ["All", "Unpaid", "Partial", "Paid"]
    )

    filtered_leads = []

    for lead in leads:
        matches_search = (
            search.lower() in lead.get("name", "").lower()
            or search.lower() in lead.get("phone", "").lower()
            or search.lower() in lead.get("address", "").lower()
        )

        matches_status = (
            status_filter == "All"
            or lead.get("status", "New") == status_filter
        )

        matches_payment = (
            payment_filter == "All"
            or lead.get("payment_status", "Unpaid") == payment_filter
        )

        if matches_search and matches_status and matches_payment:
            filtered_leads.append(lead)

    if filtered_leads:
        for index, lead in enumerate(filtered_leads):
            with st.container(border=True):
                top1, top2, top3 = st.columns([2, 1, 1])

                with top1:
                    st.subheader(lead.get("name", "No Name"))

                with top2:
                    st.write(f"**Status:** {lead.get('status', 'New')}")

                with top3:
                    st.write(f"**Balance:** ${money(lead.get('amount_owed', 0)) - money(lead.get('amount_paid', 0)):,.0f}")

                if lead.get("follow_up") == str(date.today()):
                    st.error("⚠️ FOLLOW UP TODAY")

                st.write(f"📞 **Phone:** {lead.get('phone', '')}")
                st.write(f"📍 **Address:** {lead.get('address', '')}")
                st.write(f"🏷️ **Type:** {lead.get('service', '')}")
                st.write(f"📅 **Follow-Up:** {lead.get('follow_up', 'Not set')}")
                st.write(f"💰 **Quote / Deal Value:** ${money(lead.get('quote', 0)):,.0f}")
                st.write(f"💸 **Amount Owed:** ${money(lead.get('amount_owed', 0)):,.0f}")
                st.write(f"✅ **Amount Paid:** ${money(lead.get('amount_paid', 0)):,.0f}")
                st.write(f"🧾 **Payment Status:** {lead.get('payment_status', 'Unpaid')}")
                st.write(f"👉 **Next Action:** {lead.get('next_action', '')}")
                st.write(f"📝 **Notes:** {lead.get('notes', '')}")

                if st.button("Delete Lead", key=f"delete-{index}-{lead.get('phone', '')}"):
                    leads.remove(lead)
                    save_leads(leads)
                    st.rerun()
    else:
        st.info("No leads found.")
