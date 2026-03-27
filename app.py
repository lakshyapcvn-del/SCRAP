import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

def edit_receipt(input_pdf_path, output_pdf_path, modifications):
    # 1. Open the original PDF
    doc = fitz.open(input_pdf_path)
    page = doc[0]
    
    # 2. Create a temporary PDF for the new text overlay
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Using 'Courier' as it is the closest standard PDF match to the 
    # monospaced dot-matrix font seen in the files [cite: 1, 7, 10]
    can.setFont("Courier-Bold", 10) 

    for old_text, new_text in modifications.items():
        if new_text.lower() == "no change":
            continue
            
        # Search for the specific text instances
        text_instances = page.search_for(old_text)
        
        for inst in text_instances:
            # "Whiten off" the old text by drawing a white rectangle
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
            
            # Write the new text at the same coordinates
            # We adjust slightly to maintain vertical symmetry
            can.drawString(inst.x0, inst.y0 + (inst.height * 0.2), new_text)
    
    can.save()
    packet.seek(0)
    
    # 3. Merge the overlay with the redacted original
    new_pdf = fitz.open("pdf", packet.read())
    page.show_pdf_page(page.rect, new_pdf, 0)
    
    doc.save(output_pdf_path)
    print(f"File saved successfully as {output_pdf_path}")

# --- CONFIGURATION DOMAINS ---
# Replace the values in the parentheses with your desired text
changes = {
    "SUSHILA COMPUTERISED DHARAM KANTA": "NEW HEADING HERE", # (no change)
    "UP83BT/2931": "UP32XX1234",                             # (no change)
    "DCM-6": "HEAVY TRUCK",                                   # (no change)
    "MATEARIL": "IRON SCRAP",                                # (no change)
    "15085": "16000",                                        # (no change)
    "6155": "6000",                                          # (no change)
    "8930": "10000"                                          # (no change)
}

# Run the editor
# edit_receipt("kp.pdf", "updated_receipt.pdf", changes)
