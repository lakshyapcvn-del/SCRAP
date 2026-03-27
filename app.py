import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def symmetry_pdf_editor(input_stream, modifications):
    # Open the PDF from the uploaded stream
    doc = fitz.open(stream=input_stream, filetype="pdf")
    page = doc[0]
    
    # Create an overlay in memory
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Matching the fixed-width thermal printer font (Courier-Bold)
    can.setFont("Courier-Bold", 10)

    for old_text, new_text in modifications.items():
        if not new_text or new_text.lower() == "(no change)":
            continue

        # Find the exact coordinates of the target text
        text_instances = page.search_for(old_text)

        for inst in text_instances:
            # STAGE 1: CLEAN WHITEN-OFF (The "Symmetry" Logic)
            # This masks only the text area to keep the background clean
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

            # STAGE 2: ACCURATE REWRITE
            # We use a slight vertical offset to match the original baseline
            can.drawString(inst.x0, inst.y0 + 2, new_text)

    can.save()
    packet.seek(0)

    # Merge the new text layer onto the original page
    new_pdf = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, new_pdf, 0)
    
    return doc.tobytes()

# --- INPUT YOUR CHANGES HERE ---
# If you don't want to change a field, leave it as "(no change)"
changes = {
    "SHUSHILA NEAR COMPUTRISED CHARAM KANTA": "(no change)", # **Top Heading**
    "UP82T 4786": "(no change)",                             # **vehicle no.**
    "PLASTIC": "(no change)",                                # **vehicle type/material**
    "16320": "(no change)",                                  # **gross weight**
    "6360": "(no change)",                                   # **tare weight**
    "9960": "(no change)"                                    # **net weight**
}

# Usage in Streamlit:
# if uploaded_file:
#     final_pdf = symmetry_pdf_editor(uploaded_file.read(), changes)
