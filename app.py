import streamlit as st
import json
from datetime import date
from datetime import datetime


FILE_NAME = "leads.json"

def load_leads():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_leads(leads):
    with open(FILE_NAME, "w") as file:
        json.dump(leads, file, indent=4)

st.title("Wills Tracking for Cleaning Company 💼")
st.write("Cleaning Business customer Tracker")

leads = load_leads()

st.header("Add New Lead")

name = st.text_input("Name")
phone = st.text_input("Phone")
service = st.selectbox("Service", ["Buyer Lead", "Seller Lead", "Cleaning Client", "Referral", "Other"])
status = st.selectbox("Lead Status", ["New", "Called", "Texted", "Appointment Set", "Under Contract", "Closed", "Lost"])
follow_up = st.date_input("Follow-Up Date", value=date.today())
notes = st.text_area("Notes")
quote = st.text_input("Deal Value / Cleaning Quote ($)")
next_action = st.text_input("Next Action")

if st.button("Save Lead"):
    if name and phone:
        new_lead = {
            "name": name,
            "phone": phone,
            "service": service,
            "status": status,
            "follow_up": str(follow_up),
            "notes": notes,
            "quote": quote,
            "next_action": next_action
        }

        leads.append(new_lead)
        save_leads(leads)
        st.success("Lead saved!")

    else:
        st.warning("Please enter a name and phone number.") 
       

st.divider()

st.header("Search & Filter Leads")

search = st.text_input("Search by name or phone")
status_filter = st.selectbox("Filter by status", ["All", "New", "Contacted", "Follow-Up Needed", "Closed", "Lost"])

filtered_leads = []

for lead in leads:
    matches_search = (
        search.lower() in lead.get("name", "").lower()
        or search.lower() in lead.get("phone", "").lower()
    )

    matches_status = (
        status_filter == "All"
        or lead.get("status", "New") == status_filter
    )

    if matches_search and matches_status:
        filtered_leads.append(lead)

st.header("Leads")

if filtered_leads:
    for lead in filtered_leads:
        if lead.get("follow_up") == str(date.today()):
            st.error("⚠️ FOLLOW UP TODAY")

    st.subheader(lead.get("name", "No Name"))
    st.write(f"📞 Phone: {lead.get('phone', '')}")
    st.write(f"🏢 Service: {lead.get('service', '')}")
    st.write(f"📌 Status: {lead.get('status', 'New')}")
    st.write(f"📅 Follow-Up: {lead.get('follow_up', 'Not set')}")
    st.write(f"📝 Notes: {lead.get('notes', '')}")
    st.write(f"💰 Value: {lead.get('quote', '')}")
    st.write(f"👉 Next Action: {lead.get('next_action', '')}")

    if st.button(f"Delete {lead.get('name')}", key=f"delete-{lead.get('phone')}"):
        leads.remove(lead)
        save_leads(leads)
        st.rerun()

    st.divider()
