"""
Base parser class that provides common functionality for all PDF parsers.
"""

import re
from pathlib import Path
from parsers.common import (
    extract_pdf_content, convert_to_mathjax, 
    save_questions_to_json, get_pdf_path, 
    get_output_path, show_sample_question
)

class BaseParser:
    """
    Base class for all PDF parsers with common functionality.
    """
    
    def __init__(self, pdf_filename="ElectricChargesandFields paper 01.pdf"):
        """
        Initialize the parser with the PDF file to process.
        
        Args:
            pdf_filename (str): Name of the PDF file in the input directory
        """
        self.pdf_filename = pdf_filename
        self.pdf_path = get_pdf_path(pdf_filename)
        self.parser_name = self.__class__.__name__
    
    def extract_text(self):
        """
        Extract text from the PDF file.
        
        Returns:
            str: Extracted text or None if extraction failed
        """
        if not self.pdf_path.exists():
            print(f"Error: PDF file not found at {self.pdf_path}")
            return None
        
        print(f"Processing PDF: {self.pdf_path}")
        text = extract_pdf_content(self.pdf_path)
        
        if not text:
            print("Failed to extract text from PDF")
            return None
        
        print(f"Extracted {len(text)} characters from PDF")
        return text
    
    def save_raw_text(self, text, suffix=""):
        """
        Save raw extracted text for debugging.
        
        Args:
            text (str): Raw text to save
            suffix (str): Suffix for the filename
        """
        filename = f"raw_{self.parser_name.lower()}{suffix}.txt"
        debug_path = get_output_path(filename)
        
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Raw text saved to {debug_path}")
    
    def parse_questions(self, text):
        """
        Parse questions from text. Must be implemented by subclasses.
        
        Args:
            text (str): Text to parse
            
        Returns:
            list: List of parsed questions
        """
        raise NotImplementedError("Subclasses must implement parse_questions")
    
    def save_questions(self, questions, suffix=""):
        """
        Save parsed questions to JSON file.
        
        Args:
            questions (list): List of parsed questions
            suffix (str): Suffix for the filename
        """
        filename = f"{self.parser_name.lower()}_questions{suffix}.json"
        output_path = get_output_path(filename)
        save_questions_to_json(questions, output_path)
    
    def show_sample(self, questions):
        """
        Show a sample of the first extracted question.
        
        Args:
            questions (list): List of parsed questions
        """
        show_sample_question(questions, self.parser_name)
    
    def run(self):
        """
        Main execution method that runs the complete parsing workflow.
        """
        # Extract text from PDF
        text = self.extract_text()
        if not text:
            return
        
        # Save raw text for debugging
        self.save_raw_text(text)
        
        # Parse questions
        questions = self.parse_questions(text)
        print(f"Parsed {len(questions)} questions")
        
        if not questions:
            print("No questions found. Check the raw text file for debugging.")
            return
        
        # Save questions to JSON
        self.save_questions(questions)
        
        # Show sample question
        self.show_sample(questions)
    
    def create_question_dict(self, question_text, options, answer="", solution="", max_marks=1, question_num=""):
        """
        Create a standardized question dictionary.
        
        Args:
            question_text (str): Question text
            options (dict): Dictionary with keys 'A', 'B', 'C', 'D'
            answer (str): Correct answer (A, B, C, or D)
            solution (str): Solution/explanation
            max_marks (int): Maximum marks for the question
            question_num (str): Question number
            
        Returns:
            dict: Standardized question dictionary
        """
        question_dict = {
            'question': convert_to_mathjax(question_text.strip()),
            'optionA': convert_to_mathjax(options.get('A', '').strip()),
            'optionB': convert_to_mathjax(options.get('B', '').strip()),
            'optionC': convert_to_mathjax(options.get('C', '').strip()),
            'optionD': convert_to_mathjax(options.get('D', '').strip()),
            'answer': answer,
            'max_marks': max_marks,
            'solution': convert_to_mathjax(solution.strip())
        }
        
        if question_num:
            question_dict['question_num'] = question_num
            
        return question_dict
    
    def parse_single_question(self, content, question_num=""):
        """
        Parse a single question block. Must be implemented by subclasses.
        
        Args:
            content (str): Question content to parse
            question_num (str): Question number
            
        Returns:
            dict: Parsed question dictionary or None if invalid
        """
        raise NotImplementedError("Subclasses must implement parse_single_question")
    
    def is_valid_question(self, question_dict):
        """
        Check if a question dictionary is valid.
        
        Args:
            question_dict (dict): Question dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not question_dict:
            return False
        
        # Check if question text exists
        if not question_dict.get('question'):
            return False
        
        # Check if at least one option exists
        options = [
            question_dict.get('optionA', ''),
            question_dict.get('optionB', ''),
            question_dict.get('optionC', ''),
            question_dict.get('optionD', '')
        ]
        
        return any(option.strip() for option in options) 