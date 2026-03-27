import streamlit as st
import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def process_manual_edit(input_bytes, manual_inputs):
    # Open the PDF from the uploaded bytes
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    page = doc[0]
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Using Courier-Bold to match the monospaced thermal printer font
    can.setFont("Courier-Bold", 10)

    # Physical coordinates for the 'Sushila' receipt layout
    # [x0, y0, x1, y1]
    locations = {
        "HEADING": [40, 20, 450, 50],    # The "Sushila Dharam Kaanta" area
        "VEHICLE": [155, 115, 300, 132], # Vehicle No.
        "TYPE": [155, 142, 300, 158],    # Vehicle Type/Material
        "GROSS": [45, 188, 115, 203],    # Gross Weight
        "TARE": [45, 203, 115, 218],     # Tare Weight
        "NET": [45, 218, 115, 233]       # Net Weight
    }

    for key, rect_coords in locations.items():
        new_val = manual_inputs.get(key, "")
        
        # Only process if the user actually typed something
        if new_val:
            # 1. WHITEN-OFF: Mask the original pixels
            rect = fitz.Rect(rect_coords)
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            # 2. REWRITE: Place manual text with accurate symmetry
            can.drawString(rect.x0, rect.y0 + 10, new_val)

    can.save()
    packet.seek(0)
    
    # Merge the manual overlay
    overlay = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, overlay, 0)
    
    return doc.tobytes()

# --- STREAMLIT INTERFACE ---
st.set_page_config(page_title="Manual PDF Editor")
st.title("Sushila Receipt Manual Editor")

file = st.file_uploader("Upload the receipt PDF", type="pdf")

if file:
    st.info("Click a field to type. '(no change)' will vanish automatically.")

    # MANUAL INPUT DOMAINS
    st.markdown("### **The top heading**")
    h = st.text_input("Replace 'Sushila Dharam Kaanta' text", placeholder="(no change)", key="h")
    
    st.markdown("### **vehicle no.**")
    v = st.text_input("Replace Vehicle Number", placeholder="(no change)", key="v")
    
    st.markdown("### **vehicle type**")
    t = st.text_input("Replace Material/Type", placeholder="(no change)", key="t")
    
    st.markdown("### **Weights**")
    c1, c2, c3 = st.columns(3)
    with c1:
        g = st.text_input("Gross", placeholder="(no change)", key="g")
    with c2:
        ta = st.text_input("Tare", placeholder="(no change)", key="ta")
    with c3:
        n = st.text_input("Net", placeholder="(no change)", key="n")

    manual_data = {"HEADING": h, "VEHICLE": v, "TYPE": t, "GROSS": g, "TARE": ta, "NET": n}

    if st.button("Apply Manual Changes"):
        with st.spinner("Processing symmetry..."):
            final_pdf = process_manual_edit(file.getvalue(), manual_data)
            st.success("PDF updated successfully!")
            st.download_button(
                label="Download Edited PDF",
                data=final_pdf,
                file_name="manual_edited_receipt.pdf",
                mime="application/pdf"
            )


        
