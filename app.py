import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests

# Page Configuration & Professional Styling
st.set_page_config(
    page_title="Enterprise Roster & Shift Automation Console",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 700; color: #0F172A; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #475569; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Admin Email Configuration
ADMIN_EMAILS = ["jashikasahu862@gmail.com", "yogesh@bminfotradegroup.com"]
APP_URL = "https://shift-roster-automation-nrg8ndrrz2jdtbml6txg4q.streamlit.app"

# Query Parameter Handling for Mobile Sync (Run first)
query_params = st.query_params
is_admin_from_url = query_params.get("admin") == "true"

if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = is_admin_from_url
elif is_admin_from_url:
    st.session_state.is_admin = True

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

if 'audit_logs' not in st.session_state:
    st.session_state.audit_logs = []

# Main Header
st.title("📅 Enterprise Roster Management & Secure Dispatch System")
st.write("Automated shift tracking, rotation engine, approval workflow, and multi-channel notification console.")

# Helper Functions (Email Alerts)
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

📲 Click below link to review and Approve/Reject on Mobile/PC:
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
    except Exception:
        return False

def send_employee_decision_email(emp_email, emp_name, req_date, shift, status_decision):
    sender_email = "jashikasahu862@gmail.com"
    app_password = "ezxg vper qgqa xvpb"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        subject_status = "APPROVED ✅" if status_decision == "Approved" else "REJECTED ❌"
        
        body = f"""Hello {emp_name},

Your shift change request for {req_date} has been {status_decision.upper()} by Management.

Request Details:
- Requested Shift: {shift}
- Status: {subject_status}

Regards,
Operations Team"""
        
        msg = MIMEText(body)
        msg['Subject'] = f"Shift Change Request Status: {subject_status}"
        msg['From'] = f"Roster Management <{sender_email}>"
        msg['To'] = emp_email
        
        server.sendmail(sender_email, emp_email, msg.as_string())
        server.close()
        return True
    except Exception:
        return False

# MS Teams Webhook Helper Function
def send_to_teams(table_md, date_str):
    # Enterprise Teams Webhook URL
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

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎯 Operational Controls")

# Admin Authentication Panel
if not st.session_state.is_admin:
    with st.sidebar.expander("🔒 Admin Portal Unlock"):
        pass_key = st.text_input("Enter Passkey", type="password")
        if st.button("Authenticate"):
            if pass_key == st.session_state.admin_password:
                st.session_state.is_admin = True
                st.success("Admin Session Activated")
                st.rerun()
            else:
                st.error("Invalid Authorization Key")
else:
    st.sidebar.success("🔓 Logged in as Admin (Jashika / Yogesh)")
    with st.sidebar.expander("⚙️ Security Options"):
        new_pass = st.text_input("New Passkey", type="password")
        confirm_pass = st.text_input("Confirm Passkey", type="password")
        if st.button("Update Passkey"):
            if new_pass != "" and new_pass == confirm_pass:
                st.session_state.admin_password = new_pass
                st.success("Passkey updated!")
            else:
                st.error("Passwords mismatch.")
        if st.button("Logout Admin"):
            st.session_state.is_admin = False
            st.rerun()

st.sidebar.markdown("---")
selected_date = st.sidebar.date_input("Select Schedule Date", datetime.now())
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

# Shift Rotation Engine (Admin Only)
if st.session_state.is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Shift Rotation Engine")

    if st.sidebar.button("🎲 Execute Standard Rotation"):
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

        st.sidebar.success("✅ Roster updated! (Deepak retained in General Shift)")

# Employee Request Form
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Submit Shift Override Request")

selected_emp = st.sidebar.selectbox("Select Employee", st.session_state.roster["Employee"])
current_shift = st.session_state.roster.loc[st.session_state.roster["Employee"] == selected_emp, "Regular Shift"].values[0]
current_status = st.session_state.roster.loc[st.session_state.roster["Employee"] == selected_emp, "Status"].values[0]

shift_options = ["6:00 AM – 3:00 PM", "10:00 AM – 7:00 PM", "2:00 PM – 11:00 PM", "10:00 PM – 7:00 AM"]
default_shift_idx = shift_options.index(current_shift) if current_shift in shift_options else 0
requested_shift = st.sidebar.selectbox("Requested Shift Timing", shift_options, index=default_shift_idx)

status_options = ["Working", "Weekly Off", "On Leave", "Shift Swapped"]
default_status_idx = status_options.index(current_status) if current_status in status_options else 0
requested_status = st.sidebar.selectbox("Requested Status", status_options, index=default_status_idx)

working_employees = list(st.session_state.roster[st.session_state.roster["Status"] == "Working"]["Employee"])
assigned_replacement = st.sidebar.selectbox("Assign Replacement Coverage", ["None"] + working_employees)

if st.sidebar.button("📩 Submit Change Request"):
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
    st.sidebar.success(f"✅ Request submitted! Notification sent to Admins.")

# Main Dashboard Metrics
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

# Approval Queue Display (Admin Only - Mobile & PC Synced)
if len(st.session_state.pending_requests) > 0:
    st.error("🚨 Pending Shift Change Approvals Required!")
    if st.session_state.is_admin:
        st.subheader("🛡️ Admin Approval Queue (Jashika / Yogesh)")
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
                    
                    emp_email = st.session_state.roster.at[emp_idx, "Email"]
                    send_employee_decision_email(emp_email, req['Employee'], req['Date'], req['Shift'], "Approved")
                    
                    st.session_state.audit_logs.append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Employee": req['Employee'],
                        "Date": req['Date'],
                        "Requested Shift": req['Shift'],
                        "Action": "Approved"
                    })
                    st.session_state.pending_requests.pop(idx)
                    st.success("Approved & employee notified!")
                    st.rerun()
            with col_c:
                if st.button(f"❌ Reject #{idx+1}"):
                    emp_idx = st.session_state.roster[st.session_state.roster["Employee"] == req['Employee']].index[0]
                    emp_email = st.session_state.roster.at[emp_idx, "Email"]
                    send_employee_decision_email(emp_email, req['Employee'], req['Date'], req['Shift'], "Rejected")
                    
                    st.session_state.audit_logs.append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Employee": req['Employee'],
                        "Date": req['Date'],
                        "Requested Shift": req['Shift'],
                        "Action": "Rejected"
                    })
                    st.session_state.pending_requests.pop(idx)
                    st.warning("Rejected & employee notified.")
                    st.rerun()
        st.markdown("---")

# Roster Table
st.subheader("📊 Live Shift Roster Status")
st.dataframe(st.session_state.roster[["Employee", "Email", "Regular Shift", "Weekly Off", "Status", "Replacement"]], use_container_width=True)

# Export (Admin Only)
if st.session_state.is_admin:
    csv_data = st.session_state.roster.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Roster Data (CSV/Excel)",
        data=csv_data,
        file_name=f"Roster_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

# Audit Logs (Admin Only)
if st.session_state.is_admin and len(st.session_state.audit_logs) > 0:
    st.markdown("---")
    st.subheader("📜 Operational Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)

st.markdown("---")

# Broadcast & Dispatch Console
st.subheader("📢 Shift Schedule Dispatch Console")

table_rows = [f"| **{row['Employee']}** | {row['Regular Shift']} | {row['Status']} | {row['Replacement']} |" for _, row in st.session_state.roster.iterrows()]
table_header = "| Employee | Shift Timing | Duty Status | Coverage |\n| :--- | :--- | :--- | :--- |"
markdown_table_str = table_header + "\n" + "\n".join(table_rows)

notification_text = f"**Daily Shift Operational Summary ({formatted_date_str}):**\n\n" + markdown_table_str
st.text_area("Broadcast Message Preview:", value=notification_text, height=220)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📧 Broadcast Roster via Email"):
        with st.spinner("Dispatching broadcast..."):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login("jashikasahu862@gmail.com", "ezxg vper qgqa xvpb")
                for _, row in st.session_state.roster.iterrows():
                    msg = MIMEText(f"Hello {row['Employee']},\n\nYour shift update for {formatted_date_str}:\n- Shift: {row['Regular Shift']}\n- Status: {row['Status']}\n- Coverage: {row['Replacement']}\n\nSummary:\n{notification_text}")
                    msg['Subject'] = f"📅 Daily Shift Schedule - {formatted_date_str}"
                    msg['From'] = "Roster Console <jashikasahu862@gmail.com>"
                    msg['To'] = row['Email']
                    server.sendmail("jashikasahu862@gmail.com", row['Email'], msg.as_string())
                server.close()
                st.success("✅ Broadcast emails dispatched!")
            except Exception as e:
                st.error(f"❌ Dispatch failed: {e}")

with col_btn2:
    if st.button("💬 Post Summary to MS Teams"):
        with st.spinner("Sending table to MS Teams Channel..."):
            success, msg = send_to_teams(markdown_table_str, formatted_date_str)
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ Teams Integration Error: {msg}")