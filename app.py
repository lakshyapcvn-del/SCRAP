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

# Fixed Column List to prevent "Empty Columns" error
MASTER_COLS = [
    'Date', 'Party Name', 'Location', 'Vehicle No', 'Revenue', 
    'White Scrap (Qty)', 'Green Scrap (Qty)', 'Party Rate', 
    'Mill Rate', 'Report', 'Purchase', 'Vehicle Charge', 
    'GST Purchase %', 'GST Sale %', 'Total Saving'
]

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="SCRAP", layout="wide", page_icon="🏗️")

# --- PDF ENGINE HELPER ---
def generate_pdf_report(df, label):
    try:
        from fpdf import FPDF
    except ImportError:
        st.error("Critical Error: 'fpdf' library not found. Please add 'fpdf' to requirements.txt")
        return None

    class SCRAP_PDF(FPDF):
        def header(self):
            self.set_fill_color(230, 230, 230) 
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

    pdf = SCRAP_PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    
    # PDF Column Mapping
    pdf_cols = {"Date": 22, "Vehicle": 28, "Party": 40, "Location": 25, "W.Qty": 18, "G.Qty": 18, "P.Rate": 18, "M.Rate": 18, "Report": 20, "Purch": 20, "Saving": 25}
    for title, width in pdf_cols.items():
        pdf.cell(width, 10, title, 1, 0, 'C', 1) 
    pdf.ln()
    
    pdf.set_font("Arial", '', 7)
    total_sav = 0
    for _, row in df.iterrows():
        pdf.cell(22, 10, str(row.get('Date', '')), 1)
        pdf.cell(28, 10, str(row.get('Vehicle No', '')), 1)
        pdf.cell(40, 10, str(row.get('Party Name', ''))[:22], 1)
        pdf.cell(25, 10, str(row.get('Location', '')), 1)
        pdf.cell(18, 10, str(row.get('White Scrap (Qty)', 0)), 1)
        pdf.cell(18, 10, str(row.get('Green Scrap (Qty)', 0)), 1)
        pdf.cell(18, 10, str(row.get('Party Rate', 0)), 1)
        pdf.cell(18, 10, str(row.get('Mill Rate', 0)), 1)
        pdf.cell(20, 10, f"{float(row.get('Report', 0)):,.0f}", 1)
        pdf.cell(20, 10, f"{float(row.get('Purchase', 0)):,.0f}", 1)
        s_val = float(row.get('Total Saving', 0))
        pdf.cell(25, 10, f"{s_val:,.2f}", 1)
        total_sav += s_val
        pdf.ln()
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 10, f"TOTAL NET SAVING: INR {total_sav:,.2f}", 0, 1, 'R')
    fn = f"SCRAP_Report_{label}.pdf"
    pdf.output(fn)
    return fn

# --- HEADER ---
col_t, col_c = st.columns([3, 1])
with col_t:
    st.title("🏗️ SCRAP")
with col_c:
    st.metric(label=datetime.now().strftime("%B %Y"), value=datetime.now().strftime("%d %a"))

if 'rows' not in st.session_state:
    st.session_state.rows = [{k: (0.0 if 'Rate' in k or 'Qty' in k or 'Amt' in k or 'Saving' in k or 'Revenue' in k or 'Report' in k or 'Purchase' in k or 'Charge' in k else '') for k in MASTER_COLS}]
    # Set GST Defaults
    st.session_state.rows[0]['GST Purchase %'] = 5.0
    st.session_state.rows[0]['GST Sale %'] = 18.0

# --- INPUT AREA ---
total_daily_saving = 0.0
for i, row in enumerate(st.session_state.rows):
    with st.container():
        st.markdown(f"### 🚛 Entry #{i+1}")
        c1, c2, c3, c4 = st.columns(4)
        row['Party Name'] = c1.text_input("Party Name", value=row['Party Name'], key=f"p_{i}")
        row['Location'] = c2.text_input("Location", value=row['Location'], key=f"l_{i}")
        row['Vehicle No'] = c3.text_input("Vehicle No", value=row['Vehicle No'], key=f"v_{i}")
        row['Revenue'] = c4.number_input("Revenue", value=float(row['Revenue']), key=f"r_{i}")
        
        c5, c6, c7, c8 = st.columns(4)
        row['White Scrap (Qty)'] = c5.number_input("White Qty", value=float(row['White Scrap (Qty)']), key=f"ws_{i}")
        row['Green Scrap (Qty)'] = c6.number_input("Green Qty", value=float(row['Green Scrap (Qty)']), key=f"gs_{i}")
        row['Party Rate'] = c7.number_input("P. Rate", value=float(row['Party Rate']), key=f"pr_{i}")
        row['Mill Rate'] = c8.number_input("M. Rate", value=float(row['Mill Rate']), key=f"mr_{i}")
        
        c9, c10, c11 = st.columns(3)
        row['Report'] = c9.number_input("Report Amt", value=float(row['Report']), key=f"rep_{i}")
        row['Purchase'] = c10.number_input("Purchase Amt", value=float(row['Purchase']), key=f"pur_{i}")
        row['Vehicle Charge'] = c11.number_input("Vehicle Charge", value=float(row['Vehicle Charge']), key=f"vc_{i}")

        # GST Logic
        g1, g2 = st.columns(2)
        row['GST Purchase %'] = g1.number_input("GP %", value=float(row['GST Purchase %']), key=f"gp_in_{i}")
        row['GST Sale %'] = g2.number_input("GS %", value=float(row['GST Sale %']), key=f"gs_in_{i}")

        g_in = (row['Revenue'] or 0) * (row['GST Purchase %'] / 100)
        g_out = (row['Revenue'] or 0) * (row['GST Sale %'] / 100)
        row['Total Saving'] = (row['Purchase'] - row['Report'] - row['Vehicle Charge']) + g_in + g_out
        total_daily_saving += row['Total Saving']
        st.info(f"Saving: ₹{row['Total Saving']:,.2f}")
        st.divider()

st.metric("Grand Total", f"₹ {total_daily_saving:,.2f}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Sync", "📑 History", "📊 Master"])

with tab1:
    b1, b2, b3 = st.columns(3)
    if b1.button("➕ Add Row", use_container_width=True):
        new_row = {k: (0.0 if any(x in k for x in ['Rate', 'Qty', 'Saving', 'Revenue', 'Report', 'Purchase', 'Charge']) else '') for k in MASTER_COLS}
        new_row['GST Purchase %'], new_row['GST Sale %'] = 5.0, 18.0
        st.session_state.rows.append(new_row); st.rerun()
    
    if b2.button("❌ Remove Last", use_container_width=True) and len(st.session_state.rows) > 1:
        st.session_state.rows.pop(); st.rerun()

    if b3.button("🚀 SYNC & MAIL", type="primary", use_container_width=True):
        df_save = pd.DataFrame(st.session_state.rows)
        df_save['Date'] = datetime.now().strftime("%d/%m/%Y")
        df_save = df_save[MASTER_COLS] # Force column order
        
        if os.path.exists(FULL_MASTER_PATH):
            old_df = pd.read_excel(FULL_MASTER_PATH)
            df_save = pd.concat([old_df, df_save], ignore_index=True)
        
        df_save.to_excel(FULL_MASTER_PATH, index=False)
        pdf = generate_pdf_report(pd.DataFrame(st.session_state.rows), "Today")
        st.success("Data synced to Master Excel!")

with tab2:
    if os.path.exists(FULL_MASTER_PATH):
        hist_df = pd.read_excel(FULL_MASTER_PATH)
        st.dataframe(hist_df, use_container_width=True)
    else:
        st.warning("No history found.")

with tab3:
    if os.path.exists(FULL_MASTER_PATH):
        with open(FULL_MASTER_PATH, "rb") as f:
            st.download_button("📥 Download Master.xlsx", f, file_name=MASTER_FILE)
