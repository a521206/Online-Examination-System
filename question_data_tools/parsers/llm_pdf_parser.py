"""
LLM-based PDF to Questions Parser
Uses OpenAI API to intelligently extract and parse questions from PDF files.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import openai

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None

# Add parsers directory to path for imports
parsers_dir = Path(__file__).parent
sys.path.insert(0, str(parsers_dir))

from llm_utils import (
    Question, 
    Answer, 
    extract_questions, 
    extract_answers,
    combine_questions_and_answers, 
    validate_and_enrich_questions
)
from file_utils import (
    extract_pdf_content,
    save_questions_to_json
)

# --- Utility Functions ---

# --- Main Parser Class ---

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
        
        # Define and create directories
        base_dir = Path(__file__).parent.parent
        self.input_dir = base_dir / "input"
        self.output_dir = base_dir / "output"
        self.working_dir = base_dir / "working"
        
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.working_dir.mkdir(exist_ok=True)
        
        self.restart = restart

    # --- Public API ---

    def process_all_files(self):
        """Process all PDF files in the input directory."""
        pdf_files = self._get_pdf_files()
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            print("-" * 40)
            self.process_single_file(pdf_file)
    
    def process_single_or_all_files(self, specific_file=None):
        """Process a specific PDF file if provided, else all files."""
        if specific_file:
            pdf_path = Path(specific_file)
            if not pdf_path.is_absolute():
                pdf_path = self.input_dir / pdf_path
            if not pdf_path.exists():
                print(f"File not found: {pdf_path}")
                return
            print(f"\nProcessing single file: {pdf_path.name}")
            print("-" * 40)
            self.process_single_file(pdf_path)
        else:
            self.process_all_files()

    def process_single_file(self, pdf_path):
        """Process a single PDF file, from extraction to final output."""
        paths = self._get_interim_paths(pdf_path)
        if self.restart:
            self._delete_interim_files(pdf_path)

        # Step 1: Extract text and separate content
        raw_text = self._get_raw_text(pdf_path, paths['raw'])
        questions_text, answers_text = self._separate_questions_and_answers(raw_text)

        # Step 2: Extract, combine, and enrich questions
        questions_objs = self._get_or_create_questions(
            questions_text, answers_text, paths
        )
        
        # Step 3: LLM Validation and Enrichment
        if questions_objs:
            questions_objs = self._validate_and_enrich(questions_objs)

        # Step 4: Transform and save final output
        if questions_objs:
            self._transform_and_save(questions_objs, paths['final'])
        else:
            print("No questions to process.")

    # --- File and Path Management ---

    def _get_pdf_files(self):
        """Get all PDF files from input directory."""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF file(s) in input directory:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file.name}")
        return pdf_files
    
    def _get_interim_paths(self, pdf_path):
        """Get all interim and final file paths for a given PDF."""
        stem = pdf_path.stem
        return {
            'raw': self.working_dir / f"{stem}_raw.txt",
            'questions': self.working_dir / f"{stem}_questions.json",
            'answers': self.working_dir / f"{stem}_answers.json",
            'final': self.output_dir / f"llm_questions_{stem}.json"
        }
    
    def _delete_interim_files(self, pdf_path):
        """Delete all generated files for a given PDF to allow reprocessing."""
        paths = self._get_interim_paths(pdf_path)
        for key, path in paths.items():
            if path.exists():
                path.unlink()
                print(f"Deleted {path}")

    # --- Processing Steps ---

    def _get_raw_text(self, pdf_path, raw_text_path):
        """Extract text from PDF or load from cache."""
        if raw_text_path.exists():
            print(f"Loading raw text from {raw_text_path}")
            with open(raw_text_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = extract_pdf_content(pdf_path)
            if text is not None:
                with open(raw_text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Saved raw text to {raw_text_path}")
        print(f"Extracted {len(text) if text else 0} characters from PDF")
        return text

    def _separate_questions_and_answers(self, text):
        """Separate the main text into questions and answers sections."""
        answer_indicators = [
            "ANSWERS", "ANSWER KEY", "SOLUTIONS", 
            "SOLUTION KEY", "ANSWERS AND SOLUTIONS"
        ]
        questions_text = text
        answers_text = ""
        if not text:
            return "", ""
            
        for indicator in answer_indicators:
            position = text.upper().find(indicator)
            if position != -1:
                questions_text = text[:position].strip()
                answers_text = text[position:].strip()
                print(f"Found answers section starting with: {indicator}")
                print(f"Questions: {len(questions_text)} chars, Answers: {len(answers_text)} chars")
                break
        return questions_text, answers_text

    def _get_or_create_questions(self, questions_text, answers_text, paths):
        """Load questions from cache or perform full extraction and combination."""
        if paths['final'].exists() and not self.restart:
            print(f"Loading final questions from {paths['final']}")
            with open(paths['final'], 'r', encoding='utf-8') as f:
                final_questions = json.load(f)
            return [Question(**q) for q in final_questions]

        # Extract questions
        questions_list = self._extract_from_text(
            text=questions_text, 
            cache_path=paths['questions'],
            extractor_func=extract_questions,
            data_name="questions"
        )
        questions_objs = [Question(**q) for q in questions_list] if questions_list else []
        
        # Extract and combine answers
        if answers_text:
            answers_list = self._extract_from_text(
                text=answers_text,
                cache_path=paths['answers'],
                extractor_func=extract_answers,
                data_name="answers"
            )
            answers_objs = [Answer(**a) for a in answers_list] if answers_list else []
            if questions_objs and answers_objs:
                questions_objs = combine_questions_and_answers(questions_objs, answers_objs)
        
        return questions_objs
    
    def _extract_from_text(self, text, cache_path, extractor_func, data_name):
        """Generic extractor for questions or answers, with caching."""
        if cache_path.exists():
            print(f"Loading {data_name} from {cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        if not text:
            return []
            
        extracted_data = extractor_func(text)
        print(f"Extracted {len(extracted_data)} {data_name}.")
        
        if BaseModel:
            data_dicts = [item.model_dump() for item in extracted_data]
        else:
            data_dicts = [dict(item) for item in extracted_data]

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data_dicts, f, indent=2, ensure_ascii=False)
        print(f"Saved {data_name} to {cache_path}")
        return data_dicts

    def _validate_and_enrich(self, questions_objs):
        """Run questions through LLM validation and enrichment."""
        print("Starting LLM validation and enrichment for all questions...")
        
        validated_questions = validate_and_enrich_questions(questions_objs)
        
        print("LLM validation and enrichment complete.")
        return validated_questions
    
    def _transform_and_save(self, questions_objs, final_path):
        """Apply final transformations and save the questions."""
        transformed_questions = []
        for q_obj in questions_objs:
            if BaseModel and isinstance(q_obj, BaseModel):
                qd = q_obj.model_dump()
            else:
                qd = dict(q_obj)

            is_mcq = all(qd.get(opt, '').strip() for opt in ['optionA', 'optionB', 'optionC', 'optionD'])
            has_mcq_answer = qd.get('mcq_answer', '').strip().upper() in ['A', 'B', 'C', 'D']
            
            if is_mcq and has_mcq_answer:
                qd['question_type'] = 'MCQ'
                qd['short_answer'] = ''
            else:
                qd['question_type'] = 'SHORT'
                qd['mcq_answer'] = ''
            
            # Ensure all other required fields are present
            for field in ['optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer', 'short_answer', 'solution']:
                qd.setdefault(field, '')

            # Set marks based on question type
            if qd['question_type'] == 'SHORT':
                # Ensure marks are at least 2 for short answer questions
                current_marks = qd.get('max_marks', 1)
                qd['max_marks'] = max(current_marks, 2)
            else:  # MCQ
                qd.setdefault('max_marks', 1)

            transformed_questions.append(qd)
            
        save_questions_to_json(transformed_questions, final_path)


# --- Main Execution ---

def main():
    """Main function to run the parser from the command line."""
    parser = argparse.ArgumentParser(description="LLM PDF Parser with interim file support.")
    parser.add_argument('--restart', action='store_true', help='Delete interim files and restart processing')
    parser.add_argument('--file', type=str, default=None, help='Process only the specified PDF file (by name or path)')
    args = parser.parse_args()
    
    try:
        llm_parser = LLMPDFParser(restart=args.restart)
        llm_parser.process_single_or_all_files(specific_file=args.file)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 