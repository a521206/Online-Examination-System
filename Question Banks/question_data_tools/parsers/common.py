"""
Common functionality shared across all PDF parser scripts.
"""

import os
import re
import json
from pathlib import Path
from pydantic import BaseModel

def extract_pdf_content(pdf_path):
    """
    Extract text content from PDF file with fallback support.
    """
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text
    except ImportError:
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    print(f"Processing page {page_num + 1}/{len(pdf_reader.pages)}")
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("Error: Please install either PyPDF2 or pdfplumber:")
            print("pip install PyPDF2")
            print("or")
            print("pip install pdfplumber")
            return None

def convert_to_mathjax(text):
    """
    Convert mathematical expressions to MathJax format for physics questions.
    """
    if not text:
        return text
    
    # Common mathematical conversions for physics
    conversions = [
        # Fractions - handle both a/b and (a)/(b) formats
        (r'(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)', r'\\frac{\1}{\2}'),
        (r'(\d+(?:\.\d+)?)/\s*(\d+(?:\.\d+)?)', r'\\frac{\1}{\2}'),
        
        # Subscripts - handle both x_1 and x₁ formats
        (r'(\w+)_(\w+)', r'\1_{\2}'),
        (r'(\w+)₁', r'\1_1'),
        (r'(\w+)₂', r'\1_2'),
        (r'(\w+)₃', r'\1_3'),
        
        # Superscripts - handle both x^2 and x² formats
        (r'(\w+)\^(\w+)', r'\1^{\2}'),
        (r'(\w+)²', r'\1^2'),
        (r'(\w+)³', r'\1^3'),
        
        # Square roots
        (r'√\(([^)]+)\)', r'\\sqrt{\1}'),
        (r'sqrt\(([^)]+)\)', r'\\sqrt{\1}'),
        
        # Greek letters (common physics symbols)
        (r'\\alpha', r'\\alpha'),
        (r'\\beta', r'\\beta'),
        (r'\\gamma', r'\\gamma'),
        (r'\\delta', r'\\delta'),
        (r'\\epsilon', r'\\epsilon'),
        (r'\\theta', r'\\theta'),
        (r'\\lambda', r'\\lambda'),
        (r'\\mu', r'\\mu'),
        (r'\\pi', r'\\pi'),
        (r'\\sigma', r'\\sigma'),
        (r'\\phi', r'\\phi'),
        (r'\\omega', r'\\omega'),
        (r'\\Delta', r'\\Delta'),
        (r'\\Sigma', r'\\Sigma'),
        (r'\\Omega', r'\\Omega'),
        
        # Common physics symbols
        (r'∞', r'\\infty'),
        (r'∂', r'\\partial'),
        (r'∇', r'\\nabla'),
        (r'·', r'\\cdot'),
        (r'×', r'\\times'),
        (r'÷', r'\\div'),
        (r'±', r'\\pm'),
        (r'∓', r'\\mp'),
        (r'≤', r'\\leq'),
        (r'≥', r'\\geq'),
        (r'≠', r'\\neq'),
        (r'≈', r'\\approx'),
        (r'≡', r'\\equiv'),
        (r'∝', r'\\propto'),
        
        # Scientific notation
        (r'(\d+)×10\^(\d+)', r'\1 \\times 10^{\2}'),
        (r'(\d+)e(\d+)', r'\1 \\times 10^{\2}'),
        
        # Common physics formulas
        (r'E = mc²', r'E = mc^2'),
        (r'F = ma', r'F = ma'),
        (r'v = u + at', r'v = u + at'),
        (r's = ut + ½at²', r's = ut + \\frac{1}{2}at^2'),
        
        # Units
        (r'(\d+)\s*C', r'\1 C'),
        (r'(\d+)\s*cm', r'\1 cm'),
        (r'(\d+)\s*m', r'\1 m'),
        (r'(\d+)\s*N', r'\1 N'),
        (r'(\d+)\s*V', r'\1 V'),
        (r'(\d+)\s*A', r'\1 A'),
        
        # Clean up multiple spaces
        (r'\s+', r' '),
    ]
    
    for pattern, replacement in conversions:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Wrap mathematical expressions in MathJax delimiters
    math_patterns = [
        # Fractions
        (r'\\frac\{[^}]+\}\{[^}]+\}', lambda m: f'${m.group(0)}$'),
        # Square roots
        (r'\\sqrt\{[^}]+\}', lambda m: f'${m.group(0)}$'),
        # Subscripts and superscripts
        (r'\\w+_\{\w+\}', lambda m: f'${m.group(0)}$'),
        (r'\\w+\^\{\w+\}', lambda m: f'${m.group(0)}$'),
        # Greek letters
        (r'\\[a-zA-Z]+', lambda m: f'${m.group(0)}$'),
        # Mathematical symbols
        (r'[≤≥≠≈≡∝∞∂∇·×÷±∓]', lambda m: f'${m.group(0)}$'),
        # Common physics variables
        (r'\b([Ee]lectric field)\b', r'$\1$'),
        (r'\b([Cc]harge)\b', r'$\1$'),
        (r'\b([Ff]orce)\b', r'$\1$'),
        (r'\b([Pp]otential)\b', r'$\1$'),
    ]
    
    for pattern, replacement in math_patterns:
        text = re.sub(pattern, replacement, text)
    
    return text.strip()

def clean_text(text):
    """
    Clean and normalize text.
    """
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*/\s*\d+\s*\n', '\n', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up line breaks
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def save_questions_to_json(questions, output_path):
    """
    Save parsed questions to a JSON file for review.
    """
    # Convert Pydantic models to dicts if needed
    questions = [q.model_dump() if isinstance(q, BaseModel) else q for q in questions]
    # Remove question_num from output if present
    output_questions = []
    for q in questions:
        output_q = q.copy()
        output_q.pop('question_num', None)
        output_questions.append(output_q)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_questions, f, indent=2, ensure_ascii=False)
    print(f"Questions saved to {output_path}")

def get_pdf_path(filename="ElectricChargesandFields paper 01.pdf"):
    """
    Get the path to the PDF file in the input directory.
    """
    input_dir = Path(__file__).parent.parent / "input"
    return input_dir / filename

def get_output_path(filename):
    """
    Get the path for output files in the output directory.
    """
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir / filename

def show_sample_question(questions, parser_name):
    """
    Display a sample of the first extracted question.
    """
    if not questions:
        print("No questions to show.")
        return
    print(f"\nSample extracted by {parser_name}:")
    print(json.dumps(questions[0], indent=2, ensure_ascii=False)) 