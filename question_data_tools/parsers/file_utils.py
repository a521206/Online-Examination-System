import json
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

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