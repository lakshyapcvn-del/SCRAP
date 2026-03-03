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
APP_PASSWORD = "soelepugugonpaua" 

# --- CONFIGURATION ---
SAVE_FOLDER = "scrap_data_logs" 
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="SCRAP", layout="wide", page_icon="🏗️")

# --- HEADER & DIGITAL CLOCK ---
col_title, col_clock = st.columns([3, 1])
with col_title:
    st.title("🏗️ SCRAP")
    st.markdown("#### *Advanced GST & Logistics Ledger*")
with col_clock:
    now = datetime.now()
    st.metric(label=now.strftime("%B %Y"), value=now.strftime("%d %a"), delta=now.strftime("%H:%M:%S"))

# --- SESSION STATE ---
if 'rows' not in st.session_state:
    st.session_state.rows = [{
        'Party Name': '', 'Location': '', 'Vehicle No': '', 
        'Revenue': None, 'White Scrap (Qty)': None, 'Green Scrap (Qty)': None,
        'Party Rate': None, 'Mill Rate': None, 'Report': None, 
        'Purchase': None, 'Vehicle Charge': None, 
        'GST Purchase %': 18.0, 'GST Sale %': 18.0, 'Total Saving': 0.0
    }]

def add_row():
    st.session_state.rows.append({
        'Party Name': '', 'Location': '', 'Vehicle No': '', 
        'Revenue': None, 'White Scrap (Qty)': None, 'Green Scrap (Qty)': None,
        'Party Rate': None, 'Mill Rate': None, 'Report': None, 
        'Purchase': None, 'Vehicle Charge': None, 
        'GST Purchase %': 18.0, 'GST Sale %': 18.0, 'Total Saving': 0.0
    })

def send_email_report(file_path, filename):
    try:
        msg = MIMEMultipart()
        msg['From'] = USER_EMAIL
        msg['To'] = USER_EMAIL
        msg['Subject'] = f"SCRAP LOG: {filename}"
        body = f"Daily SCRAP report attached.\nGenerated on: {datetime.now().strftime('%d %B %Y')}"
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
        st.error(f"Email Connection Error: {e}")
        return False

# --- UI INPUT AREA ---
st.write("---")
total_daily_saving = 0.0

for i, row in enumerate(st.session_state.rows):
    with st.container():
        st.markdown(f"### 🚛 Vehicle Entry #{i+1}")
        
        # Row 1: Basic Details
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        row['Party Name'] = r1_c1.text_input("Party Name", value=row['Party Name'], key=f"p_{i}")
        row['Location'] = r1_c2.text_input("Location", value=row['Location'], key=f"l_{i}")
        row['Vehicle No'] = r1_c3.text_input("Vehicle Number", value=row['Vehicle No'], key=f"v_{i}")
        row['Revenue'] = r1_c4.number_input("Total Revenue", value=row['Revenue'], key=f"r_{i}", placeholder="Enter amount...")
        
        # Row 2: Scrap & Rates
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        row['White Scrap (Qty)'] = r2_c1.number_input("White Scrap Qty", value=row['White Scrap (Qty)'], key=f"ws_{i}", placeholder="Qty...")
        row['Green Scrap (Qty)'] = r2_c2.number_input("Green Scrap Qty", value=row['Green Scrap (Qty)'], key=f"gs_{i}", placeholder="Qty...")
        row['Party Rate'] = r2_c3.number_input("Party Rate", value=row['Party Rate'], key=f"pr_{i}", placeholder="Rate...")
        row['Mill Rate'] = r2_c4.number_input("Mill Rate", value=row['Mill Rate'], key=f"mr_{i}", placeholder="Rate...")
        
        # Row 3: Financials
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        row['Report'] = r3_c1.number_input("Report Amount", value=row['Report'], key=f"rep_{i}", placeholder="Amount...")
        row['Purchase'] = r3_c2.number_input("Purchase Amount", value=row['Purchase'], key=f"pur_{i}", placeholder="Amount...")
        row['Vehicle Charge'] = r3_c3.number_input("Vehicle Charge", value=row['Vehicle Charge'], key=f"vc_{i}", placeholder="Amount...")

        # Row 4: GST Sections (Purchase vs Sale)
        st.markdown("#### 📑 GST Analysis (Incoming Amounts)")
        gst_pur_col, gst_sale_col = st.columns(2)
        
        with gst_pur_col:
            st.info("**GST PURCHASE**")
            row['GST Purchase %'] = st.number_input("Current Purchase Rate (%)", value=row['GST Purchase %'], key=f"gp_pct_{i}")
            gst_in_amt = (row['Revenue'] or 0) * (row['GST Purchase %'] / 100)
            st.write(f"Real GST Purchase Amount: **₹{gst_in_amt:,.2f}**")

        with gst_sale_col:
            st.success("**GST SALE**")
            row['GST Sale %'] = st.number_input("GST Return Rate (%)", value=row['GST Sale %'], key=f"gs_pct_{i}")
            gst_out_amt = (row['Revenue'] or 0) * (row['GST Sale %'] / 100)
            st.write(f"Real GST Sale Amount: **₹{gst_out_amt:,.2f}**")

        # CALCULATION: (Purchase Amt - Report Amt - Vehicle Charge) + GST Purchase + GST Sale
        base_calc = (row['Purchase'] or 0) - (row['Report'] or 0) - (row['Vehicle Charge'] or 0)
        row['Total Saving'] = base_calc + gst_in_amt + gst_out_amt
        total_daily_saving += row['Total Saving']
        
        st.markdown(f"### 💰 **Net Saving for Row {i+1}: ₹{row['Total Saving']:,.2f}**")
        st.divider()

# --- GRAND SUMMARY ---
st.markdown(f"## 📊 Daily Grand Total")
st.metric("Total Daily Savings (Incl. GST)", f"₹ {total_daily_saving:,.2f}")

# --- BUTTON BAR ---
footer_c1, footer_c2 = st.columns(2)
with footer_c1:
    if st.button("➕ Add Next Vehicle", use_container_width=True):
        add_row()
        st.rerun()
with footer_c2:
    if st.button("🚀 SAVE & EMAIL REPORT", type="primary", use_container_width=True):
        df = pd.DataFrame(st.session_state.rows)
        date_str = datetime.now().strftime('%d-%b-%Y')
        v_list = [str(r['Vehicle No']) for r in st.session_state.rows if r['Vehicle No']]
        v_str = "_".join(v_list) if v_list else "Log"
        filename = f"SCRAP_REPORT_{date_str}_({v_str}).csv"
        filepath = os.path.join(SAVE_FOLDER, filename)
        df.to_csv(filepath, index=False)
        if send_email_report(filepath, filename):
            st.balloons()
            st.success(f"Saved & Sent: {filename}")
        else:
            st.warning("Saved locally, but Email failed.")

with st.expander("🔍 Review Detailed Table"):
    st.table(pd.DataFrame(st.session_state.rows))
