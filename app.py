import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CREDENTIALS ---
USER_EMAIL = "lakshya.pcvn@gmail.com"
APP_PASSWORD = "up78ex2121" 

# --- CONFIGURATION ---
SAVE_FOLDER = "scrap_data_logs" 
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="SCRAP", layout="wide", page_icon="🏗️")

# --- HEADER & DIGITAL CLOCK ---
col_title, col_clock = st.columns([3, 1])

with col_title:
    st.title("🏗️ SCRAP")
    st.markdown("#### *Industrial Data Logging System*")

with col_clock:
    now = datetime.now()
    # TOP RIGHT: Date, Month and Digital Clock
    st.metric(label=now.strftime("%B %Y"), value=now.strftime("%d %a"), delta=now.strftime("%H:%M:%S"))

# --- SESSION STATE ---
if 'rows' not in st.session_state:
    st.session_state.rows = [{
        'Party Name': '', 'Location': '', 'Vehicle No': '', 
        'Revenue': 0.0, 'White Scrap (Qty)': 0.0, 'Green Scrap (Qty)': 0.0,
        'Party Rate': 0.0, 'Mill Rate': 0.0, 'Report': 0.0, 
        'Purchase': 0.0, 'Vehicle Charge': 0.0, 'GST': 0.0, 'Total Saving': 0.0
    }]

def add_row():
    st.session_state.rows.append({
        'Party Name': '', 'Location': '', 'Vehicle No': '', 
        'Revenue': 0.0, 'White Scrap (Qty)': 0.0, 'Green Scrap (Qty)': 0.0,
        'Party Rate': 0.0, 'Mill Rate': 0.0, 'Report': 0.0, 
        'Purchase': 0.0, 'Vehicle Charge': 0.0, 'GST': 0.0, 'Total Saving': 0.0
    })

def send_email_report(file_path, filename):
    try:
        msg = MIMEMultipart()
        msg['From'] = USER_EMAIL
        msg['To'] = USER_EMAIL
        msg['Subject'] = f"SCRAP LOG: {filename}"
        
        body = f"Daily report generated for: {datetime.now().strftime('%d %B %Y')}\nFilename: {filename}"
        msg.attach(MIMEText(body, 'plain'))

        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(USER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- UI INPUT AREA ---
st.write("---")

for i, row in enumerate(st.session_state.rows):
    with st.container():
        st.markdown(f"### 🚛 Vehicle Entry #{i+1}")
        
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        row['Party Name'] = r1_c1.text_input("Party Name", value=row['Party Name'], key=f"p_{i}")
        row['Location'] = r1_c2.text_input("Location", value=row['Location'], key=f"l_{i}")
        row['Vehicle No'] = r1_c3.text_input("Vehicle Number", value=row['Vehicle No'], key=f"v_{i}")
        row['Revenue'] = r1_c4.number_input("Revenue", value=row['Revenue'], key=f"r_{i}")
        
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        row['White Scrap (Qty)'] = r2_c1.number_input("White Scrap Qty", value=row['White Scrap (Qty)'], key=f"ws_{i}")
        row['Green Scrap (Qty)'] = r2_c2.number_input("Green Scrap Qty", value=row['Green Scrap (Qty)'], key=f"gs_{i}")
        row['Party Rate'] = r2_c3.number_input("Party Rate", value=row['Party Rate'], key=f"pr_{i}")
        row['Mill Rate'] = r2_c4.number_input("Mill Rate", value=row['Mill Rate'], key=f"mr_{i}")
        
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        row['Report'] = r3_c1.number_input("Report Amount", value=row['Report'], key=f"rep_{i}")
        row['Purchase'] = r3_c2.number_input("Purchase Amount", value=row['Purchase'], key=f"pur_{i}")
        row['Vehicle Charge'] = r3_c3.number_input("Vehicle Charge", value=row['Vehicle Charge'], key=f"vc_{i}")
        row['GST'] = r3_c4.number_input("Total GST", value=row['GST'], key=f"gst_{i}")

        # AUTO-CALC: Total Saving = (purchase amount-report amount-vehicle charge)
        row['Total Saving'] = row['Purchase'] - row['Report'] - row['Vehicle Charge']
        
        st.info(f"💰 **Total Saving (Row {i+1}):** {row['Total Saving']}")
        st.divider()

# --- BUTTON BAR ---
footer_c1, footer_c2 = st.columns(2)

with footer_c1:
    if st.button("➕ Add Next Vehicle", use_container_width=True):
        add_row()
        st.rerun()

with footer_c2:
    if st.button("🚀 SAVE INFO FOR TODAY", type="primary", use_container_width=True):
        df = pd.DataFrame(st.session_state.rows)
        
        # LOGIC: Generate filename with Date and Vehicle Numbers in brackets
        all_vehicles = "_".join([str(r['Vehicle No']) for r in st.session_state.rows if r['Vehicle No']])
        if not all_vehicles: all_vehicles = "No_Vehicle_No"
        
        date_str = datetime.now().strftime('%d-%b-%Y')
        filename = f"SCRAP_REPORT_{date_str}_({all_vehicles}).csv"
        filepath = os.path.join(SAVE_FOLDER, filename)
        
        # Local Folder Save
        df.to_csv(filepath, index=False)
        
        # Email Save
        if send_email_report(filepath, filename):
            st.balloons()
            st.success(f"File Saved: {filename}")
            st.success(f"Verified: Data sent to {USER_EMAIL}")
        else:
            st.warning(f"Saved locally as {filename}, but Email failed. Check App Password.")

# --- PREVIEW ---
with st.expander("📋 View Summary Table"):
    st.table(pd.DataFrame(st.session_state.rows))
