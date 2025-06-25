import json
import sys
import pdfplumber
import PyPDF2
from pathlib import Path
from PIL import Image
import io
import fitz  # PyMuPDF
import os

def extract_pdf_content(pdf_path):
    """
    Extract text content from PDF file using both pdfplumber and PyPDF2.
    Returns the output with more content.
    """
    pdfplumber_text = ""
    pypdf2_text = ""
    
    # Try pdfplumber
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                print("Extracting with pdfplumber...")
                for page_num, page in enumerate(pdf.pages):
                    print(f"pdfplumber: Processing page {page_num + 1}/{len(pdf.pages)}")
                    page_text = page.extract_text() or ""
                    pdfplumber_text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber extraction error: {e}")
    
    # Try PyPDF2
    if PyPDF2:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print("Extracting with PyPDF2...")
                for page_num, page in enumerate(pdf_reader.pages):
                    print(f"PyPDF2: Processing page {page_num + 1}/{len(pdf_reader.pages)}")
                    page_text = page.extract_text() or ""
                    pypdf2_text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
    
    # Compare and return the longer text
    pdfplumber_len = len(pdfplumber_text.strip())
    pypdf2_len = len(pypdf2_text.strip())
    
    if pdfplumber_len == 0 and pypdf2_len == 0:
        if not pdfplumber and not PyPDF2:
            print("Error: Please install either PyPDF2 or pdfplumber:")
            print("pip install PyPDF2")
            print("or")
            print("pip install pdfplumber")
        else:
            print("Error: Failed to extract text with both libraries")
        return None
    
    print(f"\nExtracted content lengths:")
    print(f"pdfplumber: {pdfplumber_len} characters")
    print(f"PyPDF2: {pypdf2_len} characters")
    
    if pdfplumber_len >= pypdf2_len:
        print("Using pdfplumber output (longer content)")
        return pdfplumber_text
    else:
        print("Using PyPDF2 output (longer content)")
        return pypdf2_text

def save_questions_to_json(questions, output_path):
    """
    Save parsed questions to a JSON file for review.
    """
    output_questions = []
    for q in questions:
        output_q = q.copy()
        output_q.pop('question_num', None)
        output_questions.append(output_q)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_questions, f, indent=2, ensure_ascii=False)
    print(f"Questions saved to {output_path}") 

def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    document = fitz.open(pdf_path)
    metadata = []
    for page_number in range(len(document)):
        page = document.load_page(page_number)
        image_list = page.get_images(full=True)
        # Extract text lines and their vertical positions
        text_lines = []
        blocks = page.get_text("blocks")
        for block in blocks:
            if block[6] == 0:  # text block
                # block: (x0, y0, x1, y1, "text", block_no, block_type, block_flags)
                lines = block[4].split("\n")
                y0 = block[1]
                y1 = block[3]
                # Estimate line height
                if len(lines) > 1:
                    line_height = (y1 - y0) / len(lines)
                else:
                    line_height = y1 - y0
                for i, line in enumerate(lines):
                    line_y0 = y0 + i * line_height
                    line_y1 = line_y0 + line_height
                    text_lines.append({
                        "text": line,
                        "y0": line_y0,
                        "y1": line_y1
                    })
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            pix = fitz.Pixmap(document, xref)
            output_image_path = os.path.join(
                output_folder,
                f"page_{page_number + 1}_img_{img_index + 1}.png"
            )
            if pix.n - pix.alpha < 4:
                pix.save(output_image_path)
            else:
                pix_no_alpha = fitz.Pixmap(fitz.csRGB, pix)
                pix_no_alpha.save(output_image_path)
                pix_no_alpha = None
            pix = None
            # Check if the image is blank using Pillow
            try:
                with Image.open(output_image_path) as im:
                    extrema = im.getextrema()
                    if isinstance(extrema, tuple):
                        if all((ex[0] == ex[1]) for ex in extrema):
                            os.remove(output_image_path)
                            continue
                    else:
                        if extrema[0] == extrema[1]:
                            os.remove(output_image_path)
                            continue
            except Exception:
                os.remove(output_image_path)
                continue
            # Get image vertical center
            img_y0 = img_info[2]
            img_y1 = img_info[4]
            img_y_center = (img_y0 + img_y1) / 2
            # Find closest text line
            closest_line_idx = None
            min_dist = float("inf")
            for idx, line in enumerate(text_lines):
                line_center = (line["y0"] + line["y1"]) / 2
                dist = abs(img_y_center - line_center)
                if dist < min_dist:
                    min_dist = dist
                    closest_line_idx = idx
            # Get before/after text
            before_text = text_lines[closest_line_idx - 1]["text"] if closest_line_idx is not None and closest_line_idx > 0 else None
            line_text = text_lines[closest_line_idx]["text"] if closest_line_idx is not None else None
            after_text = text_lines[closest_line_idx + 1]["text"] if closest_line_idx is not None and closest_line_idx < len(text_lines) - 1 else None
            metadata.append({
                "filename": output_image_path,
                "page": page_number + 1,
                "img_index": img_index + 1,
                "line_number": closest_line_idx + 1 if closest_line_idx is not None else None,
                "line_text": line_text,
                "before_text": before_text,
                "after_text": after_text
            })
    document.close()
    return metadata

def extract_images_pymupdf(pdf_path, output_dir):
    """
    Extract embedded images from a PDF using PyMuPDF (fitz) as a fallback.
    Returns metadata with filename, page, width, height, and colorspace.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF (fitz) is not installed. Cannot extract images with PyMuPDF.")
        return []
    from pathlib import Path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = []
    doc = fitz.open(pdf_path)
    for page_index in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_index)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            img_filename = f"{Path(pdf_path).stem}_p{page_index+1}_img{img_index+1}.{ext}"
            img_save_path = output_dir / img_filename
            with open(img_save_path, "wb") as f:
                f.write(image_bytes)
            metadata.append({
                "filename": str(img_filename),
                "page": page_index + 1,
                "width": base_image.get("width"),
                "height": base_image.get("height"),
                "colorspace": base_image.get("colorspace"),
            })
    return metadata 

def extract_pdf_structure(pdf_path, output_json, output_xml):
    doc = fitz.open(pdf_path)
    all_pages_json = []
    all_pages_xml = []
    for page in doc:
        # Get JSON structure
        page_json = page.get_text("json")
        all_pages_json.append(json.loads(page_json))
        # Get XML structure
        page_xml = page.get_text("xml")
        all_pages_xml.append(page_xml)
    # Save JSON structure
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_pages_json, f, indent=2, ensure_ascii=False)
    # Save XML structure
    with open(output_xml, "w", encoding="utf-8") as f:
        for xml in all_pages_xml:
            f.write(xml + "\n")
    doc.close()
    return output_json, output_xml 