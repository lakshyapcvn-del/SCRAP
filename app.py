import streamlit as st
import pandas as pd
from datetime import datetime, date
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
MASTER_FILE = f"SCRAP_Master_{datetime.now().strftime('%m_%Y')}.xlsx"
FULL_MASTER_PATH = os.path.join(SAVE_FOLDER, MASTER_FILE)

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="SCRAP", layout="wide", page_icon="🏗️")

# --- PDF ENGINE (WITH SIGNATURE & LOGO SUPPORT) ---
try:
    from fpdf import FPDF
except ImportError:
    st.error("Missing library: Install fpdf via pip.")

class SCRAP_PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        self.set_fill_color(230, 230, 230) 
        self.set_text_color(0, 0, 0)       
        self.set_font('Arial', 'B', 18)
        self.cell(0, 15, 'SCRAP (Main Server)', 1, 1, 'C', 1)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, f'Generated on: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, '__________________________', 0, 0, 'R')
        self.ln(5)
        self.cell(0, 10, 'Authorised Signatory    ', 0, 0, 'R')

def generate_pdf_report(df, label):
    pdf = SCRAP_PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    cols = {"Date": 22, "Vehicle": 28, "Party": 40, "Location": 25, "W.Qty": 18, "G.Qty": 18, "P.Rate": 18, "M.Rate": 18, "Report": 22, "Purch": 22, "Saving": 28}
    for title, width in cols.items():
        pdf.cell(width, 10, title, 1, 0, 'C', 1) 
    pdf.ln()
    pdf.set_font("Arial", '', 7)
    total_sav = 0
    for _, row in df.iterrows():
        d_str = row.get('Date', datetime.now().strftime('%d/%m/%Y'))
        pdf.cell(cols["Date"], 10, str(d_str), 1)
        pdf.cell(cols["Vehicle"], 10, str(row.get('Vehicle No', '')), 1)
        pdf.cell(cols["Party"], 10, str(row.get('Party Name', ''))[:25], 1) 
        pdf.cell(cols["Location"], 10, str(row.get('Location', '')), 1)
        pdf.cell(cols["W.Qty"], 10, str(row.get('White Scrap (Qty)', 0)), 1)
        pdf.cell(cols["G.Qty"], 10, str(row.get('Green Scrap (Qty)', 0)), 1)
        pdf.cell(cols["P.Rate"], 10, str(row.get('Party Rate', 0)), 1)
        pdf.cell(cols["M.Rate"], 10, str(row.get('Mill Rate', 0)), 1)
        pdf.cell(cols["Report"], 10, f"{float(row.get('Report', 0)):,.0f}", 1)
        pdf.cell(cols["Purch"], 10, f"{float(row.get('Purchase', 0)):,.0f}", 1)
        s_val = float(row.get('Total Saving', 0))
        pdf.cell(cols["Saving"], 10, f"{s_val:,.2f}", 1)
        total_sav += s_val
        pdf.ln()
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 10, f"TOTAL NET SAVING: INR {total_sav:,.2f}", 0, 1, 'R')
    fn = f"SCRAP_Report_{label}.pdf"
    pdf.output(fn)
    return fn

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
        'Revenue': 0.0, 'White Scrap (Qty)': 0.0, 'Green Scrap (Qty)': 0.0,
        'Party Rate': 0.0, 'Mill Rate': 0.0, 'Report': 0.0, 
        'Purchase': 0.0, 'Vehicle Charge': 0.0, 
        'GST Purchase %': 5.0,  # CHANGED: Default now 5%
        'GST Sale %': 18.0, 
        'Total Saving': 0.0
    }]

def add_row():
    st.session_state.rows.append({
        'Party Name': '', 'Location': '', 'Vehicle No': '', 
        'Revenue': 0.0, 'White Scrap (Qty)': 0.0, 'Green Scrap (Qty)': 0.0,
        'Party Rate': 0.0, 'Mill Rate': 0.0, 'Report': 0.0, 
        'Purchase': 0.0, 'Vehicle Charge': 0.0, 
        'GST Purchase %': 5.0, # Default now 5%
        'GST Sale %': 18.0, 
        'Total Saving': 0.0
    })

def send_email_report(file_path, filename):
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = USER_EMAIL, USER_EMAIL
        msg['Subject'] = f"SCRAP LOG: {filename}"
        body = f"Official Ledger Sync.\nDate: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
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
        server.send_message(msg); server.quit()
        return True
    except Exception as e:
        st.error(f"Email Connection Error: {e}"); return False

# --- UI INPUT AREA ---
st.write("---")
total_daily_saving = 0.0

for i, row in enumerate(st.session_state.rows):
    with st.container():
        st.markdown(f"### 🚛 Vehicle Entry #{i+1}")
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        row['Party Name'] = r1c1.text_input("Party Name", value=row['Party Name'], key=f"p_{i}")
        row['Location'] = r1c2.text_input("Location", value=row['Location'], key=f"l_{i}")
        row['Vehicle No'] = r1c3.text_input("Vehicle Number", value=row['Vehicle No'], key=f"v_{i}")
        row['Revenue'] = r1c4.number_input("Total Revenue", value=row['Revenue'], key=f"r_{i}")
        
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        row['White Scrap (Qty)'] = r2c1.number_input("White Scrap Qty", value=row['White Scrap (Qty)'], key=f"ws_{i}")
        row['Green Scrap (Qty)'] = r2c2.number_input("Green Scrap Qty", value=row['Green Scrap (Qty)'], key=f"gs_{i}")
        row['Party Rate'] = r2c3.number_input("Party Rate", value=row['Party Rate'], key=f"pr_{i}")
        row['Mill Rate'] = r2c4.number_input("Mill Rate", value=row['Mill Rate'], key=f"mr_{i}")
        
        r3c1, r3c2, r3c3 = st.columns(3)
        row['Report'] = r3c1.number_input("Report Amount", value=row['Report'], key=f"rep_{i}")
        row['Purchase'] = r3c2.number_input("Purchase Amount", value=row['Purchase'], key=f"pur_{i}")
        row['Vehicle Charge'] = r3c3.number_input("Vehicle Charge", value=row['Vehicle Charge'], key=f"vc_{i}")

        st.markdown("#### 📑 GST Analysis")
        gst_pur_col, gst_sale_col = st.columns(2)
        with gst_pur_col:
            row['GST Purchase %'] = st.number_input("Purchase GST %", value=row['GST Purchase %'], key=f"gp_pct_{i}")
            gst_in_amt = (row['Revenue'] or 0) * (row['GST Purchase %'] / 100)
            st.write(f"GST Purchase: **₹{gst_in_amt:,.2f}**")
        with gst_sale_col:
            row['GST Sale %'] = st.number_input("Sale GST %", value=row['GST Sale %'], key=f"gs_pct_{i}")
            gst_out_amt = (row['Revenue'] or 0) * (row['GST Sale %'] / 100)
            st.write(f"GST Sale: **₹{gst_out_amt:,.2f}**")

        # CALCULATION
        base_calc = (row['Purchase'] or 0) - (row['Report'] or 0) - (row['Vehicle Charge'] or 0)
        row['Total Saving'] = base_calc + gst_in_amt + gst_out_amt
        total_daily_saving += row['Total Saving']
        st.markdown(f"### 💰 **Saving: ₹{row['Total Saving']:,.2f}**")
        st.divider()

# --- SUMMARY & ACTIONS ---
st.metric("Total Daily Savings (Incl. GST)", f"₹ {total_daily_saving:,.2f}")

tab1, tab2, tab3 = st.tabs(["🚀 Sync & Send", "📑 Range History", "📊 Master Data"])

with tab1:
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add Next Vehicle", use_container_width=True):
        add_row(); st.rerun()
    if col_btn2.button("🚀 SAVE & EMAIL REPORT", type="primary", use_container_width=True):
        current_df = pd.DataFrame(st.session_state.rows)
        current_df['Date'] = datetime.now().strftime("%d/%m/%Y")
        
        # Save to Master Excel
        if os.path.exists(FULL_MASTER_PATH):
            current_df = pd.concat([pd.read_excel(FULL_MASTER_PATH), current_df], ignore_index=True)
        current_df.to_excel(FULL_MASTER_PATH, index=False)
        
        # Generate PDF
        pdf_name = f"SCRAP_{datetime.now().strftime('%d_%b_%H%M')}"
        pdf_path = generate_pdf_report(pd.DataFrame(st.session_state.rows), pdf_name)
        
        if send_email_report(pdf_path, f"{pdf_name}.pdf"):
            st.balloons(); st.success("Synced and Emailed successfully!")

with tab2:
    st.subheader("Generate PDF for Date Range")
    sd, ed = st.date_input("Start Date"), st.date_input("End Date")
    if st.button("🔎 Generate Range PDF", use_container_width=True):
        if os.path.exists(FULL_MASTER_PATH):
            mdf = pd.read_excel(FULL_MASTER_PATH)
            mdf['ParsedDate'] = pd.to_datetime(mdf['Date'], format='%d/%m/%Y').dt.date
            fdf = mdf[(mdf['ParsedDate'] >= sd) & (mdf['ParsedDate'] <= ed)].drop(columns=['ParsedDate'])
            if not fdf.empty:
                r_path = generate_pdf_report(fdf, f"Range_{sd}_to_{ed}")
                with open(r_path, "rb") as f: st.download_button("📥 Download PDF", f, file_name=f"Range_{sd}_{ed}.pdf")
            else: st.warning("No data found for this range.")

with tab3:
    if st.button("📥 Download Master.xlsx", use_container_width=True):
        if os.path.exists(FULL_MASTER_PATH):
            with open(FULL_MASTER_PATH, "rb") as f: st.download_button("📥 Click to Save Master", f, file_name=MASTER_FILE)

with st.expander("🔍 Review Detailed Table"):
    st.table(pd.DataFrame(st.session_state.rows))
