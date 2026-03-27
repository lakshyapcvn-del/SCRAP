import streamlit as st
import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def process_receipt_by_coordinates(input_bytes, changes):
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    page = doc[0]
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    can.setFont("Courier-Bold", 10)

    # These coordinates are mapped specifically to the layout of your 'SHUSHILA' receipts
    # [x0, y0, x1, y1] -> The box to whiten and rewrite
    locations = {
        "HEADING": [50, 20, 400, 45],    # Top Heading area
        "VEHICLE": [150, 115, 280, 130], # Vehicle No area
        "MATERIAL": [150, 140, 280, 155], # Material area
        "GROSS": [50, 185, 120, 200],    # Gross Weight area
        "TARE": [50, 200, 120, 215],     # Tare Weight area
        "NET": [50, 215, 120, 230]       # Net Weight area
    }

    for key, rect_coords in locations.items():
        new_text = changes.get(key, "(no change)")
        if new_text == "(no change)":
            continue
            
        # 1. WHITEN: Cleanly mask the specific physical area
        rect = fitz.Rect(rect_coords)
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()

        # 2. REWRITE: Place new text exactly in that box
        can.drawString(rect.x0, rect.y0 + 10, new_text)

    can.save()
    packet.seek(0)
    
    overlay = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, overlay, 0)
    return doc.tobytes()

# --- STREAMLIT UI WITH BOLD HEADINGS ---
st.title("Symmetry PDF Editor")
file = st.file_uploader("Upload Receipt", type="pdf")

if file:
    # DOMAINS
    st.markdown("### **The top heading**")
    h = st.text_input("New Heading", value="(no change)")
    
    st.markdown("### **vehicle no.**")
    v = st.text_input("New Vehicle No", value="(no change)")
    
    st.markdown("### **vehicle type/material**")
    m = st.text_input("New Material", value="(no change)")
    
    st.markdown("### **Weights**")
    g = st.text_input("Gross Weight", value="(no change)")
    ta = st.text_input("Tare Weight", value="(no change)")
    n = st.text_input("Net Weight", value="(no change)")

    user_data = {"HEADING": h, "VEHICLE": v, "MATERIAL": m, "GROSS": g, "TARE": ta, "NET": n}

    if st.button("Generate Accurate PDF"):
        final_pdf = process_receipt_by_coordinates(file.read(), user_data)
        st.download_button("Download Now", final_pdf, "edited_receipt.pdf")
