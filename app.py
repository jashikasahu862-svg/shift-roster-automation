import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests

# Page Configuration
st.set_page_config(
    page_title="Enterprise Shift & Roster Automation Console",
    page_icon="📅",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 30px; font-weight: 700; color: #1E293B; margin-bottom: 0px; }
    .sub-title { font-size: 15px; color: #64748B; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# Admin / Approver Email IDs
ADMIN_EMAILS = ["jashikasahu862@gmail.com", "yogesh@bminfotradegroup.com"]

# Exact Live App URL
APP_URL = "https://shift-roster-automation-nrg8ndrrz2jdtbml6txg4q.streamlit.app"

# Permanent Session State Initializations
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'roster' not in st.session_state:
    raw_df = pd.DataFrame([
        {"Employee": "Deepak", "Email": "deepak@bminfotradegroup.com", "Regular Shift": "10:00 AM – 7:00 PM", "Weekly Off": "Sunday", "Status": "Working", "Replacement": "None"},
        {"Employee": "Jashika", "Email": "jashika.sahu@bminfotradegroup.com", "Regular Shift": "2:00 PM – 11:00 PM", "Weekly Off": "Thursday", "Status": "Working", "Replacement": "None"},
        {"Employee": "Nitin", "Email": "nitin@bminfotradegroup.com", "Regular Shift": "6:00 AM – 3:00 PM", "Weekly Off": "Tuesday", "Status": "Working", "Replacement": "None"},
        {"Employee": "Pravin", "Email": "pravin@bminfotradegroup.com", "Regular Shift": "10:00 PM – 7:00 AM", "Weekly Off": "Saturday", "Status": "Working", "Replacement": "None"},
        {"Employee": "Pritam", "Email": "pritam@bminfotradegroup.com", "Regular Shift": "10:00 AM – 7:00 PM", "Weekly Off": "Sunday", "Status": "Working", "Replacement": "None"},
        {"Employee": "Rajat Kumawat", "Email": "rajat@bminfotradegroup.com", "Regular Shift": "2:00 PM – 11:00 PM", "Weekly Off": "Thursday", "Status": "Working", "Replacement": "None"}
    ])
    st.session_state.roster = raw_df.sort_values(by="Employee").reset_index(drop=True)

if 'pending_requests' not in st.session_state:
    st.session_state.pending_requests = []

# Cross-Device Parameter Logic for Mobile Browsers
try:
    params = st.query_params
    if params.get("admin") == "true":
        st.session_state.is_admin = True
except Exception:
    pass

# Header
st.title("📅 Enterprise Roster Management & Secure Dispatch System")
st.write("Automated shift tracking, rotation engine, approval workflow, and multi-channel notification console.")

# Helper Email Alert
def send_admin_alert_email(req_data):
    sender_email = "jashikasahu862@gmail.com"
    app_password = "ezxg vper qgqa xvpb"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        
        direct_approval_url = f"{APP_URL}?admin=true"
        
        body = f"""Hello Admin,

A new shift change request requires your approval:

- Employee: {req_data['Employee']}
- Date: {req_data['Date']}
- Requested Shift: {req_data['Shift']}
- Requested Status: {req_data['Status']}
- Replacement Coverage: {req_data['Replacement']}

📲 Click below link to review and Approve/Reject:
{direct_approval_url}

Regards,
Roster Automation System"""
        
        for admin_email in ADMIN_EMAILS:
            msg = MIMEText(body)
            msg['Subject'] = f"🚨 URGENT: Shift Change Approval Request - {req_data['Employee']}"
            msg['From'] = f"Roster Security Alert <{sender_email}>"
            msg['To'] = admin_email
            server.sendmail(sender_email, admin_email, msg.as_string())
            
        server.close()
        return True
    except Exception as e:
        return False

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎯 Shift Adjustment Controls")

# SIDEBAR ADMIN UNLOCK & PASSKEY CHANGE SYSTEM
st.sidebar.markdown("---")
admin_key_input = st.sidebar.text_input("🔑 Admin Unlock Key", type="password", help="Enter admin key to unlock approval queue")

if admin_key_input == st.session_state.admin_password or st.session_state.is_admin:
    st.session_state.is_admin = True
    st.sidebar.success("🔓 Admin Approval Mode Active")
    
    with st.sidebar.expander("⚙️ Change Admin Passkey"):
        new_pass = st.text_input("Enter New Passkey", type="password")
        confirm_pass = st.text_input("Confirm New Passkey", type="password")
        if st.button("Update Passkey"):
            if new_pass != "" and new_pass == confirm_pass:
                st.session_state.admin_password = new_pass
                st.success("✅ Passkey updated successfully!")
            else:
                st.error("❌ Passwords do not match or empty.")

st.sidebar.markdown("---")
selected_date = st.sidebar.date_input("Select Roster Date", datetime.now())
formatted_date_str = selected_date.strftime("%d-%b-%Y (%A)")
selected_day_name = selected_date.strftime("%A")

# Auto-update Weekly Off Status
if 'last_selected_date' not in st.session_state or st.session_state.last_selected_date != selected_date:
    st.session_state.last_selected_date = selected_date
    for idx, row in st.session_state.roster.iterrows():
        if row["Weekly Off"].strip().lower() == selected_day_name.strip().lower():
            st.session_state.roster.at[idx, "Status"] = "Weekly Off"
            st.session_state.roster.at[idx, "Replacement"] = "None"
        else:
            if st.session_state.roster.at[idx, "Status"] == "Weekly Off":
                st.session_state.roster.at[idx, "Status"] = "Working"

# ⚡ 1-CLICK POST-5th NOV SCHEDULER (DEEPAK FIXED IN GENERAL SHIFT)
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ 1-Click Post-5th Nov Scheduler")

if st.sidebar.button("🎲 Execute Standard Shift Rotation"):
    shift_rotation_map = {
        "6:00 AM – 3:00 PM": "10:00 AM – 7:00 PM",
        "10:00 AM – 7:00 PM": "2:00 PM – 11:00 PM",
        "2:00 PM – 11:00 PM": "10:00 PM – 7:00 AM",
        "10:00 PM – 7:00 AM": "6:00 AM – 3:00 PM"
    }

    shift_to_off_map = {
        "6:00 AM – 3:00 PM": "Tuesday",
        "10:00 AM – 7:00 PM": "Sunday",
        "2:00 PM – 11:00 PM": "Thursday",
        "10:00 PM – 7:00 AM": "Saturday"
    }

    for idx, row in st.session_state.roster.iterrows():
        emp_name = row["Employee"]
        
        # FIXED RULE FOR DEEPAK
        if emp_name == "Deepak":
            st.session_state.roster.at[idx, "Regular Shift"] = "10:00 AM – 7:00 PM"
            st.session_state.roster.at[idx, "Weekly Off"] = "Sunday"
            new_off = "Sunday"
        else:
            current_s = row["Regular Shift"]
            new_s = shift_rotation_map.get(current_s, "10:00 AM – 7:00 PM")
            new_off = shift_to_off_map.get(new_s, "Sunday")

            st.session_state.roster.at[idx, "Regular Shift"] = new_s
            st.session_state.roster.at[idx, "Weekly Off"] = new_off

        if new_off.strip().lower() == selected_day_name.strip().lower():
            st.session_state.roster.at[idx, "Status"] = "Weekly Off"
            st.session_state.roster.at[idx, "Replacement"] = "None"
        else:
            st.session_state.roster.at[idx, "Status"] = "Working"

    st.sidebar.success("✅ Shifts rotated! (Deepak fixed in General Shift)")

# --- SECURE INDIVIDUAL OVERRIDE REQUEST ---
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Request Shift Change")

selected_emp = st.sidebar.selectbox("Select Employee", st.session_state.roster["Employee"])

current_shift = st.session_state.roster.loc[st.session_state.roster["Employee"] == selected_emp, "Regular Shift"].values[0]
current_status = st.session_state.roster.loc[st.session_state.roster["Employee"] == selected_emp, "Status"].values[0]

shift_options = [
    "6:00 AM – 3:00 PM",
    "10:00 AM – 7:00 PM",
    "2:00 PM – 11:00 PM",
    "10:00 PM – 7:00 AM"
]

default_shift_idx = shift_options.index(current_shift) if current_shift in shift_options else 0
requested_shift = st.sidebar.selectbox("Requested Shift Timing", shift_options, index=default_shift_idx)

status_options = ["Working", "Weekly Off", "On Leave", "Shift Swapped"]
default_status_idx = status_options.index(current_status) if current_status in status_options else 0
requested_status = st.sidebar.selectbox("Requested Duty Status", status_options, index=default_status_idx)

working_employees = list(st.session_state.roster[st.session_state.roster["Status"] == "Working"]["Employee"])
assigned_replacement = st.sidebar.selectbox("Assign Replacement Coverage", ["None"] + working_employees)

if st.sidebar.button("📩 Submit Change Request for Approval"):
    req_data = {
        "Employee": selected_emp,
        "Shift": requested_shift,
        "Status": requested_status,
        "Replacement": assigned_replacement,
        "Date": formatted_date_str,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.pending_requests.append(req_data)
    
    send_admin_alert_email(req_data)
    st.sidebar.success(f"✅ Request submitted successfully! Sent for Admin approval.")

# --- DASHBOARD METRICS ---
col1, col2, col3 = st.columns(3)
working_cnt = len(st.session_state.roster[st.session_state.roster["Status"] == "Working"])
off_cnt = len(st.session_state.roster[st.session_state.roster["Status"] != "Working"])

with col1:
    st.metric("Total Workforce On-Duty", f"{working_cnt} Members")
with col2:
    st.metric("Members Off / On Leave", f"{off_cnt} Members")
with col3:
    st.metric("Selected Schedule Date", formatted_date_str)

st.markdown("---")

# APPROVAL QUEUE DISPLAY (MOBILE + DESKTOP FULLY SYNCED)
if len(st.session_state.pending_requests) > 0:
    st.error("🚨 Pending Shift Change Approvals Required!")
    
    if st.session_state.is_admin:
        st.subheader("🛡️ Admin Approval Queue (Jashika / Yogesh Sir)")
        for idx, req in enumerate(st.session_state.pending_requests):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.write(f"📌 **{req['Employee']}** requested change for **{req['Date']}** $\rightarrow$ Shift: **{req['Shift']}** | Status: **{req['Status']}** | Replacement: **{req['Replacement']}**")
            with col_b:
                if st.button(f"✅ Approve #{idx+1}"):
                    emp_idx = st.session_state.roster[st.session_state.roster["Employee"] == req['Employee']].index[0]
                    st.session_state.roster.at[emp_idx, "Regular Shift"] = req['Shift']
                    st.session_state.roster.at[emp_idx, "Status"] = req['Status']
                    st.session_state.roster.at[emp_idx, "Replacement"] = req['Replacement']
                    
                    st.session_state.pending_requests.pop(idx)
                    st.success("Change approved & roster updated!")
                    st.rerun()
            with col_c:
                if st.button(f"❌ Reject #{idx+1}"):
                    st.session_state.pending_requests.pop(idx)
                    st.warning("Change request rejected.")
                    st.rerun()
        st.markdown("---")

st.subheader("📊 Live Shift Roster Status")
st.dataframe(st.session_state.roster[["Employee", "Email", "Regular Shift", "Weekly Off", "Status", "Replacement"]], use_container_width=True)

st.markdown("---")

# AUTOMATED BROADCAST PREVIEW
st.subheader("📢 Automated Shift Notifications")

table_rows = []
for _, row in st.session_state.roster.iterrows():
    emp = row["Employee"]
    shift = row["Regular Shift"]
    status = row["Status"]
    replacement = row["Replacement"]
    table_rows.append(f"| **{emp}** | {shift} | {status} | {replacement} |")

table_header = "| Employee | Status | Shift Timing | Coverage / Replacement |\n| :--- | :--- | :--- | :--- |"
markdown_table_str = table_header + "\n" + "\n".join(table_rows)

notification_text = f"**Daily Shift Operational Summary ({formatted_date_str}):**\n\n" + markdown_table_str

st.text_area("Individual Employee Shift Broadcast Preview:", value=notification_text, height=240)

# DISPATCH LOGIC
def send_emails_to_all(summary_text, roster_df, date_str):
    sender_email = "jashikasahu862@gmail.com"
    app_password = "ezxg vper qgqa xvpb"
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        
        for _, row in roster_df.iterrows():
            emp_name = row["Employee"]
            emp_email = row["Email"]
            
            body = f"Hello {emp_name},\n\nHere is your shift status update for {date_str}:\n\n- Duty Status: {row['Status']}\n- Shift Timing: {row['Regular Shift']}\n- Assigned Coverage: {row['Replacement']}\n\nOverall Team Roster Summary:\n----------------------------------------\n{summary_text}\n\nBest regards,\nOperations Team"
            
            msg = MIMEText(body)
            msg['Subject'] = f"📅 Daily Shift Schedule Update - {date_str}"
            msg['From'] = f"Shift Automation Console <{sender_email}>"
            msg['To'] = emp_email
            
            server.sendmail(sender_email, emp_email, msg.as_string())
            
        server.close()
        return True, "Emails successfully dispatched to all employees!"
    except Exception as e:
        return False, str(e)

def send_to_teams(table_md, date_str):
    teams_webhook_url = "https://default43b2ab88f668409fba768db3e53453.ae.environment.api.powerplatform.com:443/workflows/..."
    
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptivecard.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"📋 Daily Shift Schedule - {date_str}",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": table_md,
                            "wrap": True,
                            "spacing": "Medium"
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(teams_webhook_url, json=payload)
        if response.status_code in [200, 202]:
            return True, "Successfully posted roster table to MS Teams Channel!"
        else:
            return False, f"Failed with status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

# DISPATCH BUTTONS
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📧 Dispatch via Email Broadcast"):
        with st.spinner("Dispatching emails..."):
            success, msg = send_emails_to_all(notification_text, st.session_state.roster, formatted_date_str)
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ Email Error: {msg}")

with col_btn2:
    if st.button("💬 Dispatch to MS Teams / Webhook"):
        with st.spinner("Sending table to MS Teams..."):
            success, msg = send_to_teams(notification_text, formatted_date_str)
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ Teams Error: {msg}")