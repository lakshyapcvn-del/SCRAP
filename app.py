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

# COLUMN DEFINITIONS - MUST MATCH EXACTLY
MASTER_COLS = [
    'Date', 'Party Name', 'Location', 'Vehicle No', 'Revenue', 
    'White Scrap (Qty)', 'Green Scrap (Qty)', 'Party Rate', 
    'Mill Rate', 'Report', 'Purchase', 'Vehicle Charge', 
    'GST Purchase %', 'GST Sale %', 'Total Saving'
]

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="SCRAP", layout="wide", page_icon="🏗️")

# --- PDF ENGINE ---
def generate_pdf_report(df, label):
    try:
        from fpdf import FPDF
    except ImportError:
        st.error("Missing 'fpdf' library.")
        return None

    class SCRAP_PDF(FPDF):
        def header(self):
            self.set_fill_color(230, 230, 230) 
            self.set_font('Arial', 'B', 16)
            self.cell(0, 15, 'SCRAP (Main Server) - Official Ledger', 1, 1, 'C', 1)
            self.set_font('Arial', 'I', 10)
            self.cell(0, 8, f'Report Label: {label} | Generated: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-25)
            self.set_font('Arial', 'B', 10)
            self.cell(0, 10, 'Authorised Signatory: __________________________', 0, 0, 'R')

    pdf = SCRAP_PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    
    pdf_cols = {"Date": 22, "Vehicle": 28, "Party": 40, "Location": 25, "W.Qty": 18, "G.Qty": 18, "P.Rate": 18, "M.Rate": 18, "Report": 20, "Purch": 20, "Saving": 25}
    for title, width in pdf_cols.items():
        pdf.cell(width, 10, title, 1, 0, 'C', 1) 
    pdf.ln()
    
    pdf.set_font("Arial", '', 7)
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
        pdf.cell(25, 10, f"{float(row.get('Total Saving', 0)):,.2f}", 1)
        pdf.ln()
    
    fn = f"SCRAP_Report_{label.replace(' ', '_')}.pdf"
    pdf.output(fn)
    return fn

# --- HEADER ---
col_t, col_c = st.columns([3, 1])
with col_t:
    st.title("🏗️ SCRAP")
with col_c:
    st.metric(label=datetime.now().strftime("%B %Y"), value=datetime.now().strftime("%d %a"))

if 'rows' not in st.session_state:
    st.session_state.rows = [{k: (0.0 if any(x in k for x in ['Rate', 'Qty', 'Saving', 'Revenue', 'Report', 'Purchase', 'Charge']) else '') for k in MASTER_COLS if k != 'Date'}]
    st.session_state.rows[0]['GST Purchase %'], st.session_state.rows[0]['GST Sale %'] = 5.0, 18.0

# --- MAIN INPUT ---
total_daily_saving = 0.0
for i, row in enumerate(st.session_state.rows):
    with st.container():
        st.markdown(f"### 🚛 Entry #{i+1}")
        c1, c2, c3, c4 = st.columns(4)
        row['Party Name'] = c1.text_input("Party", value=row['Party Name'], key=f"p_name_{i}")
        row['Location'] = c2.text_input("Loc", value=row['Location'], key=f"p_loc_{i}")
        row['Vehicle No'] = c3.text_input("Veh No", value=row['Vehicle No'], key=f"p_veh_{i}")
        row['Revenue'] = c4.number_input("Rev", value=float(row['Revenue']), key=f"p_rev_{i}")
        
        c5, c6, c7, c8 = st.columns(4)
        row['White Scrap (Qty)'] = c5.number_input("White Qty", value=float(row['White Scrap (Qty)']), key=f"p_w_{i}")
        row['Green Scrap (Qty)'] = c6.number_input("Green Qty", value=float(row['Green Scrap (Qty)']), key=f"p_g_{i}")
        row['Party Rate'] = c7.number_input("P.Rate", value=float(row['Party Rate']), key=f"p_pr_{i}")
        row['Mill Rate'] = c8.number_input("M.Rate", value=float(row['Mill Rate']), key=f"p_mr_{i}")
        
        c9, c10, c11 = st.columns(3)
        row['Report'] = c9.number_input("Rep Amt", value=float(row['Report']), key=f"p_rep_{i}")
        row['Purchase'] = c10.number_input("Pur Amt", value=float(row['Purchase']), key=f"p_pur_{i}")
        row['Vehicle Charge'] = c11.number_input("V.Chg", value=float(row['Vehicle Charge']), key=f"p_vchg_{i}")

        g1, g2 = st.columns(2)
        row['GST Purchase %'] = g1.number_input("GP%", value=float(row['GST Purchase %']), key=f"p_gp_{i}")
        row['GST Sale %'] = g2.number_input("GS%", value=float(row['GST Sale %']), key=f"p_gs_{i}")

        g_in = (row['Revenue'] * (row['GST Purchase %']/100))
        g_out = (row['Revenue'] * (row['GST Sale %']/100))
        row['Total Saving'] = (row['Purchase'] - row['Report'] - row['Vehicle Charge']) + g_in + g_out
        total_daily_saving += row['Total Saving']
        st.info(f"Saving: ₹{row['Total Saving']:,.2f}")
        st.divider()

st.markdown(f"## 📊 Total Daily Saving: ₹ {total_daily_saving:,.2f}")

# --- ACTION BUTTONS ---
f1, f2, f3 = st.columns(3)
with f1:
    if st.button("➕ Add Row", use_container_width=True):
        new_row = {k: (0.0 if any(x in k for x in ['Rate', 'Qty', 'Saving', 'Revenue', 'Report', 'Purchase', 'Charge']) else '') for k in MASTER_COLS if k != 'Date'}
        new_row['GST Purchase %'], new_row['GST Sale %'] = 5.0, 18.0
        st.session_state.rows.append(new_row); st.rerun()
with f2:
    if st.button("❌ Remove Last", use_container_width=True) and len(st.session_state.rows) > 1:
        st.session_state.rows.pop(); st.rerun()
with f3:
    if st.button("🚀 SYNC TO MASTER", type="primary", use_container_width=True):
        final_df = pd.DataFrame(st.session_state.rows)
        final_df['Date'] = datetime.now().strftime("%d/%m/%Y")
        final_df = final_df[MASTER_COLS] # Force columns
        
        if os.path.exists(FULL_MASTER_PATH):
            existing_df = pd.read_excel(FULL_MASTER_PATH)
            # Filter out any purely empty rows from existing data
            existing_df = existing_df.dropna(how='all')
            final_df = pd.concat([existing_df, final_df], ignore_index=True)
        
        final_df.to_excel(FULL_MASTER_PATH, index=False)
        st.balloons(); st.success(f"Successfully saved {len(st.session_state.rows)} records to Master Excel!")

# --- DOWNLOAD CENTER ---
st.write("---")
t_pdf, t_excel = st.tabs(["📄 PDF Reports", "📊 Excel Master"])

with t_pdf:
    p1, p2 = st.columns(2)
    if p1.button("Prepare Today's PDF"):
        tdf = pd.DataFrame(st.session_state.rows)
        tdf['Date'] = datetime.now().strftime("%d/%m/%Y")
        path = generate_pdf_report(tdf, f"Daily_{date.today()}")
        with open(path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=path)
    
    with p2:
        sd, ed = st.date_input("Start"), st.date_input("End")
        if st.button("Gen Range PDF"):
            if os.path.exists(FULL_MASTER_PATH):
                mdf = pd.read_excel(FULL_MASTER_PATH)
                mdf['Date_Obj'] = pd.to_datetime(mdf['Date'], format='%d/%m/%Y').dt.date
                fdf = mdf[(mdf['Date_Obj'] >= sd) & (mdf['Date_Obj'] <= ed)]
                if not fdf.empty:
                    path = generate_pdf_report(fdf, f"Range_{sd}_{ed}")
                    with open(path, "rb") as f: st.download_button("📥 Download Range PDF", f, file_name=path)

with t_excel:
    if os.path.exists(FULL_MASTER_PATH):
        master_data = pd.read_excel(FULL_MASTER_PATH)
        st.write("Current Master Records:", len(master_data))
        st.dataframe(master_data.tail(10)) # Show last 10 entries for proof
        with open(FULL_MASTER_PATH, "rb") as f:
            st.download_button("📥 Download Master.xlsx", f, file_name=MASTER_FILE)
    else:
        st.warning("Master file hasn't been created yet. Hit 'SYNC TO MASTER' above.")
