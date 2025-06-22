"""
LLM-based PDF to Questions Parser
Uses OpenAI API to intelligently extract and parse questions from PDF files.
"""

import os
import sys
from pathlib import Path

# Add parsers directory to path for imports
parsers_dir = Path(__file__).parent
sys.path.insert(0, str(parsers_dir))

from common import extract_pdf_content, save_questions_to_json
from llm_utils import call_openai_api_main
import openai

class LLMPDFParser:
    """
    LLM-based PDF parser using OpenAI API for intelligent question extraction.
    """
    
    def __init__(self):
        """Initialize the LLM parser."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = self.api_key
        self.input_dir = Path(__file__).parent.parent / "input"
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_filename_pattern = "llm_questions_{}.json"
    
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
    
    def process_all_files(self):
        """Process all PDF files in the input directory."""
        pdf_files = self.get_pdf_files()
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            print("-" * 40)
            self.process_single_file(pdf_file)
    
    def process_single_file(self, pdf_path):
        """Process a single PDF file."""
        # Extract text from PDF
        text = extract_pdf_content(pdf_path)
        print(f"Extracted {len(text)} characters from PDF")
        
        # Pre-process to separate questions and answers
        questions_text, answers_text = self._separate_questions_and_answers(text)
        
        # Check if text is too long for OpenAI
        if len(questions_text) > 12000:
            print(f"Questions text too long ({len(questions_text)} chars) for OpenAI API. Skipping this file.")
            return
        
        # Parse questions using LLM
        print("Using OpenAI API to parse questions...")
        questions = call_openai_api_main(questions_text, answers_text)
        
        if not questions:
            print("No questions extracted")
            return
        
        print(f"Extracted {len(questions)} questions")
        
        # Save questions to JSON
        output_path = self.get_output_path(pdf_path)
        save_questions_to_json(questions, output_path)
        
        # Show sample question
        if questions:
            print("\nSample question:")
            print(f"Question: {questions[0].question[:100]}...")
            print(f"Options: A) {questions[0].optionA[:50]}...")
            print(f"Answer: {questions[0].answer}")
    
    def _separate_questions_and_answers(self, text):
        """Separate questions and answers sections from text."""
        # Look for common answer section indicators
        answer_indicators = [
            "ANSWERS",
            "ANSWER KEY",
            "SOLUTIONS",
            "SOLUTION KEY",
            "ANSWERS AND SOLUTIONS"
        ]
        
        questions_text = text
        answers_text = ""
        
        # Find where answers section starts
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
    """Main function to run the LLM PDF parser."""
    parser = LLMPDFParser()
    parser.process_all_files()

if __name__ == "__main__":
    main() 