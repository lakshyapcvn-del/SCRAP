import streamlit as st
import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def process_receipt_final(input_bytes, changes):
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    page = doc[0]
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    # Accurate font match for the thermal printer style
    can.setFont("Courier-Bold", 10)

    # Physical coordinates for 'kp.pdf' layout
    locations = {
        "HEADING": [45, 25, 420, 48],    
        "VEHICLE": [155, 115, 300, 132], 
        "MATERIAL": [155, 142, 300, 158], 
        "GROSS": [45, 188, 110, 203],    
        "TARE": [45, 203, 110, 218],     
        "NET": [45, 218, 110, 233]       
    }

    for key, rect_coords in locations.items():
        new_text = changes.get(key, "")
        # If the user left it empty (the placeholder vanished), we don't change it
        if not new_text:
            continue
            
        # 1. WHITEN-OFF: Surgical removal of old pixels
        rect = fitz.Rect(rect_coords)
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()

        # 2. REWRITE: Clean symmetry placement
        can.drawString(rect.x0, rect.y0 + 10, new_text)

    can.save()
    packet.seek(0)
    
    overlay = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, overlay, 0)
    return doc.tobytes()

# --- STREAMLIT UI ---
st.title("Symmetry PDF Editor")
file = st.file_uploader("Upload Receipt (PDF)", type="pdf")

if file:
    # Using 'placeholder' so the text vanishes automatically when you click/type
    st.markdown("### **The top heading**")
    h = st.text_input("Edit Heading", placeholder="(no change)", key="h")
    
    st.markdown("### **vehicle no.**")
    v = st.text_input("Edit Vehicle No", placeholder="(no change)", key="v")
    
    st.markdown("### **vehicle type/material**")
    m = st.text_input("Edit Material", placeholder="(no change)", key="m")
    
    st.markdown("### **Weights**")
    col1, col2, col3 = st.columns(3)
    with col1:
        g = st.text_input("Gross", placeholder="(no change)", key="g")
    with col2:
        ta = st.text_input("Tare", placeholder="(no change)", key="ta")
    with col3:
        n = st.text_input("Net", placeholder="(no change)", key="n")

    user_data = {"HEADING": h, "VEHICLE": v, "MATERIAL": m, "GROSS": g, "TARE": ta, "NET": n}

    if st.button("Generate Accurate PDF"):
        # We read the file once here
        final_pdf = process_receipt_final(file.getvalue(), user_data)
        st.success("Changes processed cleanly!")
        st.download_button("Download Edited PDF", final_pdf, "edited_receipt.pdf")
