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
    Extract text content from PDF file with fallback support.
    """
    if pdfplumber:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text
    elif PyPDF2:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                print(f"Processing page {page_num + 1}/{len(pdf_reader.pages)}")
                text += page.extract_text() + "\n"
        return text
    else:
        print("Error: Please install either PyPDF2 or pdfplumber:")
        print("pip install PyPDF2")
        print("or")
        print("pip install pdfplumber")
        return None

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