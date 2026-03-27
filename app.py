import streamlit as st
import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def edit_pdf_logic(input_bytes, modifications):
    # Load the PDF from bytes
    doc = fitz.open(stream=input_bytes, filetype="pdf")
    page = doc[0]
    
    # Create an overlay in memory
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Matching the fixed-width thermal printer font
    can.setFont("Courier-Bold", 10)

    for old_text, new_text in modifications.items():
        if not new_text or new_text.upper() == "(NO CHANGE)":
            continue

        # Search for text (using 'hit_max' to ensure we find all fragments)
        text_instances = page.search_for(old_text)

        if not text_instances:
            # Try a partial search if full search fails
            short_search = old_text.split()[-1] 
            text_instances = page.search_for(short_search)

        for inst in text_instances:
            # 1. WHITEN: Cleanly mask the old text
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

            # 2. REWRITE: Align with the thermal printer baseline
            can.drawString(inst.x0, inst.y0 + 2, new_text)

    can.save()
    packet.seek(0)

    # Merge layers
    new_layer = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, new_layer, 0)
    
    return doc.tobytes()

# --- STREAMLIT UI ---
st.title("Symmetry PDF Editor")

uploaded_file = st.file_uploader("Upload your receipt PDF", type="pdf")

if uploaded_file:
    st.subheader("Edit Domains")
    
    # DOMAINS BASED ON YOUR FILES
    new_h = st.text_input("**The top heading**", value="(no change)")
    new_v = st.text_input("**vehicle no.**", value="(no change)")
    new_t = st.text_input("**vehicle type**", value="(no change)")
    new_m = st.text_input("**material**", value="(no change)")
    new_g = st.text_input("**gross weight**", value="(no change)")
    new_ta = st.text_input("**tare weight**", value="(no change)")
    new_n = st.text_input("**net weight**", value="(no change)")

    mapping = {
        "SHUSHILA NEAR COMPUTRISED CHARAM KANTA": new_h,
        "UP82T 4786": new_v,
        "DCM-6": new_t,
        "PLASTIC": new_m,
        "16320": new_g,
        "6360": new_ta,
        "9960": new_n
    }

    if st.button("Generate Accurate PDF"):
        result_pdf = edit_pdf_logic(uploaded_file.read(), mapping)
        
        st.download_button(
            label="Download Edited PDF",
            data=result_pdf,
            file_name="edited_receipt.pdf",
            mime="application/pdf"
        )
