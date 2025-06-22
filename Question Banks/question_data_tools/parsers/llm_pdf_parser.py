"""
LLM-based PDF to Questions Parser
Uses OpenAI API to intelligently extract and parse questions from PDF files.
"""

import os
import sys
from pathlib import Path
import json
import argparse

# Add parsers directory to path for imports
parsers_dir = Path(__file__).parent
sys.path.insert(0, str(parsers_dir))

from llm_utils import call_openai_api_main
import openai

# --- Inline extract_pdf_content ---
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

# --- Inline save_questions_to_json ---
def save_questions_to_json(questions, output_path):
    """
    Save parsed questions to a JSON file for review.
    """
    # Convert Pydantic models to dicts if needed
    try:
        from pydantic import BaseModel
        questions = [q.model_dump() if isinstance(q, BaseModel) else q for q in questions]
    except ImportError:
        pass
    # Remove question_num from output if present
    output_questions = []
    for q in questions:
        output_q = q.copy()
        output_q.pop('question_num', None)
        output_questions.append(output_q)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_questions, f, indent=2, ensure_ascii=False)
    print(f"Questions saved to {output_path}")

class LLMPDFParser:
    """
    LLM-based PDF parser using OpenAI API for intelligent question extraction.
    """
    
    def __init__(self, restart=False):
        """Initialize the LLM parser."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = self.api_key
        self.input_dir = Path(__file__).parent.parent / "input"
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_filename_pattern = "llm_questions_{}.json"
        self.restart = restart
    
    def get_pdf_files(self):
        """Get all PDF files from input directory."""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF file(s) in input directory:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file.name}")
        return pdf_files
    
    def get_output_path(self, pdf_path):
        """Get output path for a given PDF file."""
        output_filename = self.output_filename_pattern.format(pdf_path.stem)
        return self.output_dir / output_filename

    def get_interim_paths(self, pdf_path):
        stem = pdf_path.stem
        return {
            'raw': self.output_dir / f"{stem}_raw.txt",
            'questions': self.output_dir / f"{stem}_questions.json",
            'answers': self.output_dir / f"{stem}_answers.json",
            'final': self.get_output_path(pdf_path)
        }
    
    def delete_interim_files(self, pdf_path):
        paths = self.get_interim_paths(pdf_path)
        for key, path in paths.items():
            if path.exists():
                path.unlink()
                print(f"Deleted {path}")

    def process_all_files(self):
        pdf_files = self.get_pdf_files()
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            print("-" * 40)
            self.process_single_file(pdf_file)
    
    def process_single_file(self, pdf_path):
        paths = self.get_interim_paths(pdf_path)
        if self.restart:
            self.delete_interim_files(pdf_path)

        # Step 1: Extract text from PDF
        if paths['raw'].exists():
            print(f"Loading raw text from {paths['raw']}")
            with open(paths['raw'], 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = extract_pdf_content(pdf_path)
            with open(paths['raw'], 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Saved raw text to {paths['raw']}")
        print(f"Extracted {len(text)} characters from PDF")
        
        # Step 2: Separate questions and answers
        questions_text, answers_text = self._separate_questions_and_answers(text)

        # Step 3: Extract questions
        questions = None
        if paths['questions'].exists():
            print(f"Loading questions from {paths['questions']}")
            with open(paths['questions'], 'r', encoding='utf-8') as f:
                questions = json.load(f)
        else:
            from llm_utils import extract_questions
            questions = extract_questions(questions_text)
            print(f"Extracted {len(questions)} questions.")
            # Convert to dicts for JSON serialization
            questions_dicts = [q.model_dump() if hasattr(q, 'model_dump') else dict(q) for q in questions]
            with open(paths['questions'], 'w', encoding='utf-8') as f:
                json.dump(questions_dicts, f, indent=2, ensure_ascii=False)
            print(f"Saved questions to {paths['questions']}")
            questions = questions_dicts

        # Step 4: Extract answers (if any)
        answers = None
        if answers_text:
            if paths['answers'].exists():
                print(f"Loading answers from {paths['answers']}")
                with open(paths['answers'], 'r', encoding='utf-8') as f:
                    answers = json.load(f)
            else:
                from llm_utils import extract_answers
                answers = extract_answers(answers_text)
                print(f"Extracted {len(answers)} answers.")
                # Convert to dicts for JSON serialization
                answers_dicts = [a.model_dump() if hasattr(a, 'model_dump') else dict(a) for a in answers]
                with open(paths['answers'], 'w', encoding='utf-8') as f:
                    json.dump(answers_dicts, f, indent=2, ensure_ascii=False)
                print(f"Saved answers to {paths['answers']}")
                answers = answers_dicts

        # Step 4.5: Always merge answers into questions if answers exist
        from llm_utils import Question, Answer, combine_questions_and_answers, generate_solutions_for_questions
        if questions and isinstance(questions[0], dict):
            questions_objs = [Question(**q) for q in questions]
        else:
            questions_objs = questions
        if answers:
            if isinstance(answers[0], dict):
                answers_objs = [Answer(**a) for a in answers]
            else:
                answers_objs = answers
            questions_objs = combine_questions_and_answers(questions_objs, answers_objs)

        # Step 4.6: For MCQs and SHORT questions with missing or too-short solutions, use LLM to fill in a short solution
        def needs_solution(q):
            sol = q.solution or ''
            return (not sol.strip() or len(sol.strip().split()) < 5) and (
                (q.question_type == 'MCQ' and q.mcq_answer in ['A', 'B', 'C', 'D']) or
                (q.question_type == 'SHORT' and q.short_answer and q.short_answer.strip())
            )
        questions_missing_solutions = [q for q in questions_objs if needs_solution(q)]
        if questions_missing_solutions:
            n_mcq = sum(1 for q in questions_missing_solutions if q.question_type == 'MCQ')
            n_short = sum(1 for q in questions_missing_solutions if q.question_type == 'SHORT')
            print(f"Generating solutions for {n_mcq} MCQ and {n_short} SHORT questions with missing or too-short solutions...")
            from llm_utils import generate_solutions_for_questions
            solutions = generate_solutions_for_questions(questions_missing_solutions)
            for q, sol in zip(questions_missing_solutions, solutions):
                q.solution = sol

        # Step 5: Transform and save final output
        transformed_questions = []
        for q in questions_objs:
            qd = q if isinstance(q, dict) else q.model_dump() if hasattr(q, 'model_dump') else dict(q)
            is_mcq = all(qd.get(opt, '').strip() for opt in ['optionA', 'optionB', 'optionC', 'optionD'])
            has_mcq_answer = qd.get('mcq_answer', '').strip().upper() in ['A', 'B', 'C', 'D']
            if is_mcq and has_mcq_answer:
                qd['question_type'] = 'MCQ'
                qd['short_answer'] = ''
            else:
                qd['question_type'] = 'SHORT'
                qd['mcq_answer'] = ''
            qd.pop('answer', None)
            qd.pop('question_num', None)
            for opt in ['optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer', 'short_answer', 'solution']:
                if opt not in qd:
                    qd[opt] = ''
            if 'max_marks' not in qd:
                qd['max_marks'] = 1
            transformed_questions.append(qd)
        save_questions_to_json(transformed_questions, paths['final'])
        if transformed_questions:
            print("\nSample question:")
            print(f"Question: {transformed_questions[0]['question'][:100]}...")
            print(f"Options: A) {transformed_questions[0]['optionA'][:50]}...")
            print(f"Type: {transformed_questions[0]['question_type']}")
            print(f"MCQ Answer: {transformed_questions[0]['mcq_answer']}")
            print(f"Short Answer: {transformed_questions[0]['short_answer']}")

    def _extract_questions_and_answers(self, questions_text, answers_text):
        from llm_utils import extract_questions, extract_answers
        questions = extract_questions(questions_text)
        print(f"Extracted {len(questions)} questions.")
        answers = None
        if answers_text:
            answers = extract_answers(answers_text)
            print(f"Extracted {len(answers)} answers.")
        return questions, answers

    def _separate_questions_and_answers(self, text):
        answer_indicators = [
            "ANSWERS",
            "ANSWER KEY",
            "SOLUTIONS",
            "SOLUTION KEY",
            "ANSWERS AND SOLUTIONS"
        ]
        questions_text = text
        answers_text = ""
        for indicator in answer_indicators:
            if indicator in text.upper():
                position = text.upper().find(indicator)
                if position != -1:
                    questions_text = text[:position].strip()
                    answers_text = text[position:].strip()
                    print(f"Found answers section starting with: {indicator}")
                    print(f"Questions: {len(questions_text)} chars, Answers: {len(answers_text)} chars")
                    break
        return questions_text, answers_text

def main():
    parser = argparse.ArgumentParser(description="LLM PDF Parser with interim file support.")
    parser.add_argument('--restart', action='store_true', help='Delete interim files and restart processing')
    args = parser.parse_args()
    llm_parser = LLMPDFParser(restart=args.restart)
    llm_parser.process_all_files()

if __name__ == "__main__":
    main() 