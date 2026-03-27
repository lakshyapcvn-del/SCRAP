import fitz  # PyMuPDF
import io
from reportlab.pdfgen import canvas

def edit_receipt_symmetry(input_path, output_path, changes):
    # Open the original PDF
    doc = fitz.open(input_path)
    page = doc[0]
    
    # Create an overlay layer in memory
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Matching the fixed-width thermal printer font found in the images
    can.setFont("Courier-Bold", 9) 

    for old_text, new_text in changes.items():
        if new_text.lower() == "(no change)":
            continue
            
        # 1. Locate the text on the page
        text_instances = page.search_for(old_text)
        
        for inst in text_instances:
            # 2. WHITEN: Mask the old text with a white rectangle to maintain background
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
            
            # 3. REWRITE: Place new text exactly in the same bounding box
            # Vertical adjustment (+2) to align with thermal printer baseline
            can.drawString(inst.x0, inst.y0 + 2, new_text)
    
    can.save()
    packet.seek(0)
    
    # Merge the overlay onto the redacted page
    new_layer = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, new_layer, 0)
    
    doc.save(output_path)
    print(f"File generated: {output_path}")

# --- INPUT DOMAINS ---
# Replace the text in the parentheses below with your desired updates
modifications = {
    # Top Heading 
    "SHUSHILA NEAR COMPUTRISED CHARAM KANTA": "(no change)", 
    
    # Vehicle and Commodity Info 
    "UP82T 4786": "(no change)",        # vehicle no.
    "DCM-6": "(no change)",             # vehicle type (from photo)
    "PLASTIC": "(no change)",           # commodity/material 
    
    # Weight Data 
    "16320": "(no change)",             # gross weight
    "6360": "(no change)",              # tare weight
    "9960": "(no change)"               # net weight
}

# Execution
# edit_receipt_symmetry("kp.pdf", "final_receipt.pdf", modifications)
