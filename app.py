import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def process_receipt(input_pdf, output_pdf, mapping):
    # Open the document
    doc = fitz.open(input_pdf)
    
    for page_layout in doc:
        # Create a overlay PDF in memory
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_layout.rect.width, page_layout.rect.height))
        
        # Using Courier as it matches the fixed-width thermal font in the images
        can.setFont("Courier-Bold", 10)

        for old_text, new_text in mapping.items():
            if not new_text or new_text.lower() == "no change":
                continue

            # Find coordinates of the text to be replaced
            text_instances = page_layout.search_for(old_text)

            for inst in text_instances:
                # 1. CLEANLY WHITEN: Draw a white rectangle over the old text
                # This acts as the "white-off" tape
                page_layout.add_redact_annot(inst, fill=(1, 1, 1))
                page_layout.apply_redactions()

                # 2. REWRITE: Place new text at the same spot
                # Small vertical offset (+2) to align with the thermal print baseline
                can.drawString(inst.x0, inst.y0 + 2, new_text)

        can.save()
        packet.seek(0)

        # Merge the new text layer onto the page
        overlay = fitz.open("pdf", packet.read())
        page_layout.show_pdf_page(page_layout.rect, overlay, 0)

    doc.save(output_pdf)
    doc.close()

# --- INPUT YOUR CHANGES HERE ---
# Based on the font analysis of SHUSHILA DHARAM KANTA receipts
replacements = {
    "SHUSHILA NEAR COMPUTRISED CHARAM KANTA": "YOUR NEW HEADING", # Top Heading
    "UP82T 4786": "VEHICLE NO",                                  # Vehicle No.
    "PLASTIC": "VEHICLE TYPE/MATERIAL",                          # Material
    "16320": "NEW GROSS",                                        # Gross Weight
    "6360": "NEW TARE",                                          # Tare Weight
    "9960": "NEW NET"                                            # Net Weight
}

# To run:
# process_receipt("kp.pdf", "final_output.pdf", replacements)
