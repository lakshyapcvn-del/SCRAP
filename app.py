import streamlit as st
import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def process_symmetry_pdf(input_bytes, changes):
    # Open the PDF from the upload stream
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    page = doc[0]
    
    # Create an overlay for the new text
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Using Courier-Bold to match the monospaced thermal printer font
    can.setFont("Courier-Bold", 10)

    # Physical coordinates mapped to 'SUSHILA' receipt layout
    # Format: [x0, y0, x1, y1]
    locations = {
        "HEADING": [40, 20, 450, 50],    # Area for 'SUSHILA COMPUTERISED...'
        "VEHICLE": [155, 115, 300, 132], # Area for Vehicle Number
        "TYPE": [155, 142, 300, 158],    # Area for Vehicle Type/Material
        "GROSS": [45, 188, 115, 203],    # Area for Gross Weight value
        "TARE": [45, 203, 115, 218],     # Area for Tare Weight value
        "NET": [45, 218, 115, 233]       # Area for Net Weight value
    }

    for key, rect_coords in locations.items():
        new_text = changes.get(key, "")
        
        # If the user left it empty (the placeholder vanished), skip replacement
        if not new_text:
            continue
            
        # 1. WHITEN-OFF: Mask the specific area to maintain document symmetry
        rect = fitz.Rect(rect_coords)
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()

        # 2. REWRITE: Place the new command text precisely
        # Vertical adjustment (+10) ensures it sits on the original line
        can.drawString(rect.x0, rect.y0 + 10, new_text)

    can.save()
    packet.seek(0)
    
    # Merge the rewritten layer back into the original PDF
    overlay = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, overlay, 0)
    
    return doc.tobytes()

# --- STREAMLIT UI ---
st.title("Symmetry PDF Editor")

file = st.file_uploader("Upload Receipt PDF", type="pdf")

if file:
    st.info("Click any box to replace the text. Leaving it empty keeps the original.")

    # DOMAIN SECTIONS WITH BOLD HEADINGS
    st.markdown("### **The top heading (Sushila Dharam kaanta)**")
    h = st.text_input("New Heading", placeholder="(no change)", key="h")
    
    st.markdown("### **vehicle no.**")
    v = st.text_input("New Vehicle No", placeholder="(no change)", key="v")
    
    st.markdown("### **vehicle type**")
    t = st.text_input("New Type/Material", placeholder="(no change)", key="t")
    
    st.markdown("### **Weights**")
    col1, col2, col3 = st.columns(3)
    with col1:
        g = st.text_input("Gross", placeholder="(no change)", key="g")
    with col2:
        ta = st.text_input("Tare", placeholder="(no change)", key="ta")
    with col3:
        n = st.text_input("Net", placeholder="(no change)", key="n")

    user_inputs = {
        "HEADING": h, "VEHICLE": v, "TYPE": t, 
        "GROSS": g, "TARE": ta, "NET": n
    }

    if st.button("Generate Accurate PDF"):
        # Process using the uploaded file's bytes
        output_pdf = process_symmetry_pdf(file.getvalue(), user_inputs)
        
        st.success("Symmetry processing complete.")
        st.download_button(
            label="Download Edited PDF",
            data=output_pdf,
            file_name="edited_sushila_receipt.pdf",
            mime="application/pdf"
        )
        
