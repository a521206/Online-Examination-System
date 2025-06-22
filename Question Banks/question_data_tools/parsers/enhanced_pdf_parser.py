"""
Enhanced PDF to Questions Parser
Extracts questions from PDF files with advanced parsing logic and better MathJax handling.
"""

import re
from parsers.base_parser import BaseParser

class EnhancedPDFParser(BaseParser):
    """
    Enhanced PDF parser with advanced text processing and better MathJax handling.
    """
    
    def parse_questions(self, text):
        """
        Parse questions from text using enhanced pattern matching.
        
        Args:
            text (str): Text to parse
            
        Returns:
            list: List of parsed questions
        """
        questions = []
        
        # Split into potential question blocks
        # Look for numbered questions (1., 2., etc.)
        question_blocks = re.split(r'\n\s*(\d+)\.\s*', text)
        
        for i in range(1, len(question_blocks), 2):  # Skip first empty block, then alternate
            if i + 1 >= len(question_blocks):
                break
                
            question_num = question_blocks[i]
            question_content = question_blocks[i + 1]
            
            if not question_content.strip():
                continue
            
            # Parse the question content
            parsed = self.parse_single_question(question_content, question_num)
            if parsed and self.is_valid_question(parsed):
                questions.append(parsed)
        
        return questions
    
    def parse_single_question(self, content, question_num=""):
        """
        Parse a single question block into structured format with enhanced logic.
        
        Args:
            content (str): Question content to parse
            question_num (str): Question number
            
        Returns:
            dict: Parsed question dictionary or None if invalid
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        question_text = ""
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        answer = ""
        solution = ""
        
        current_section = "question"
        current_option = None
        
        for line in lines:
            # Detect question text (lines before options)
            if current_section == "question":
                if re.match(r'^[A-D]\)', line) or re.match(r'^[a-d]\)', line):
                    current_section = "options"
                    current_option = line[0].upper()
                    options[current_option] = line[2:].strip()
                else:
                    question_text += line + " "
                continue
            
            # Handle options
            if current_section == "options":
                if re.match(r'^[A-D]\)', line) or re.match(r'^[a-d]\)', line):
                    current_option = line[0].upper()
                    option_text = line[2:].strip()
                    options[current_option] = option_text
                elif current_option and options[current_option]:
                    # Continue current option
                    options[current_option] += " " + line
                else:
                    # Might be solution or answer
                    if re.match(r'^Answer:', line, re.IGNORECASE):
                        answer = line.split(':', 1)[1].strip()
                        current_section = "solution"
                    elif re.match(r'^Solution:', line, re.IGNORECASE):
                        solution = line.split(':', 1)[1].strip()
                        current_section = "solution"
                    else:
                        solution += line + " "
                        current_section = "solution"
                continue
            
            # Handle solution
            if current_section == "solution":
                solution += line + " "
        
        return self.create_question_dict(
            question_text=question_text,
            options=options,
            answer=answer,
            solution=solution,
            question_num=question_num
        )

def main():
    """
    Main function to run the enhanced PDF parser.
    """
    parser = EnhancedPDFParser()
    parser.run()

if __name__ == "__main__":
    main() 