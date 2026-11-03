import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
import urllib.parse
import random

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

# Authorized Admin Email List
ADMIN_EMAILS = ["jashikasahu862@gmail.com", "yogesh@bminfotradegroup.com"]
APP_URL = "https://shift-roster-automation-nrg8ndrrz2jdtbml6txg4q.streamlit.app"

# Query Parameter Handling for Cross-Device Request Sync
query_params = st.query_params
is_admin_from_url = query_params.get("admin") == "true"
url_req_emp = query_params.get("req_emp")
url_req_shift = query_params.get("req_shift")
url_req_status = query_params.get("req_status")
url_req_rep = query_params.get("req_rep")
url_req_date = query_params.get("req_date")

if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = is_admin_from_url
elif is_admin_from_url:
    st.session_state.is_admin = True

if 'otp_code' not in st.session_state:
    st.session_state.otp_code = None

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

# Inject incoming email request params into pending queue
if url_req_emp and url_req_shift:
    incoming_req = {
        "Employee": url_req_emp,
        "Shift": url_req_shift,
        "Status": url_req_status if url_req_status else "Working",
        "Replacement": url_req_rep if url_req_rep else "None",
        "Date": url_req_date if url_req_date else datetime.now().strftime("%d-%b-%Y (%A)"),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if incoming_req not in st.session_state.pending_requests:
        st.session_state.pending_requests.append(incoming_req)

if 'audit_logs' not in st.session_state:
    st.session_state.audit_logs = []

st.title("📅 Enterprise Roster Management & Secure Dispatch System")
st.write("Automated shift tracking, rotation engine, approval workflow, and multi-channel notification console.")

# Helper Functions
def send_otp_email(target_email, otp):
    sender_email = "jashikasahu862@gmail.com"
    app_password = "ezxg vper qgqa xvpb"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        body = f"""Hello Admin,

Your Security Password Reset OTP is: {otp}

Enter this OTP in the application sidebar to update your Admin Passkey.

Best regards,
Roster Security Team"""
        msg = MIMEText(body)
        msg['Subject'] = f"🔑 Admin Password Reset OTP: {otp}"
        msg['From'] = f"Roster Security Console <{sender_email}>"
        msg['To'] = target_email
        server.sendmail(sender_email, target_email, msg.as_string())
        server.close()
        return True
    except Exception:
        return False

def send_admin_alert_email(req_data):
    sender_email = "jashikasahu862@gmail.com"
    app_password = "ezxg vper qgqa xvpb"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        
        encoded_emp = urllib.parse.quote(req_data['Employee'])
        encoded_shift = urllib.parse.quote(req_data['Shift'])
        encoded_status = urllib.parse.quote(req_data['Status'])
        encoded_rep = urllib.parse.quote(req_data['Replacement'])
        encoded_date = urllib.parse.quote(req_data['Date'])
        
        direct_approval_url = f"{APP_URL}?admin=true&req_emp={encoded_emp}&req_shift={encoded_shift}&req_status={encoded_status}&req_rep={encoded_rep}&req_date={encoded_date}"
        
        body = f"""Hello Admin,

A new shift change request requires your approval:

- Employee: {req_data['Employee']}
- Date: {req_data['Date']}
- Requested Shift: {req_data['Shift']}
- Requested Status: {req_data['Status']}
- Replacement Coverage: {req_data['Replacement']}

📲 Click below link to open approval queue directly on Mobile/PC:
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

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎯 Operational Controls")

# Admin Authentication & Forgot Password Section
if not st.session_state.is_admin:
    with st.sidebar.expander("🔒 Admin Portal Access"):
        admin_email_input = st.text_input("Admin Email Address")
        pass_key = st.text_input("Passkey", type="password")
        
        if st.button("Authenticate Admin"):
            if admin_email_input.strip().lower() in [e.lower() for e in ADMIN_EMAILS] and pass_key == st.session_state.admin_password:
                st.session_state.is_admin = True
                st.success("Admin Session Activated")
                st.rerun()
            else:
                st.error("Access Denied: Invalid Admin Email or Passkey!")
        
        st.markdown("---")
        st.write("❓ **Forgot Passkey?**")
        reset_email = st.text_input("Enter Email to Receive OTP")
        if st.button("Send Reset OTP"):
            if reset_email.strip().lower() in [e.lower() for e in ADMIN_EMAILS]:
                generated_otp = str(random.randint(100000, 999999))
                st.session_state.otp_code = generated_otp
                if send_otp_email(reset_email.strip(), generated_otp):
                    st.success(f"✅ OTP sent to {reset_email}!")
                else:
                    st.error("❌ Email sending failed.")
            else:
                st.error("❌ Unauthorized email address.")
        
        if st.session_state.otp_code:
            entered_otp = st.text_input("Enter 6-Digit OTP")
            new_forgot_pass = st.text_input("New Passkey", type="password")
            if st.button("Reset & Login"):
                if entered_otp == st.session_state.otp_code and new_forgot_pass != "":
                    st.session_state.admin_password = new_forgot_pass
                    st.session_state.is_admin = True
                    st.session_state.otp_code = None
                    st.success("✅ Passkey updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP or empty passkey.")
else:
    st.sidebar.success("🔓 Admin Mode Active (Jashika / Yogesh)")
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

# Auto-update Weekly Off
if 'last_selected_date' not in st.session_state or st.session_state.last_selected_date != selected_date:
    st.session_state.last_selected_date = selected_date
    for idx, row in st.session_state.roster.iterrows():
        if row["Weekly Off"].strip().lower() == selected_day_name.strip().lower():
            st.session_state.roster.at[idx, "Status"] = "Weekly Off"
            st.session_state.roster.at[idx, "Replacement"] = "None"
        else:
            if st.session_state.roster.at[idx, "Status"] == "Weekly Off":
                st.session_state.roster.at[idx, "Status"] = "Working"

# Shift Rotation (Admin Only)
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
    st.sidebar.success(f"✅ Request submitted! Direct approval alert sent to Admins.")

# Dashboard Metrics
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

# Approval Queue Display
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

# Broadcast Console
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
        st.info("Teams Webhook integration ready.")