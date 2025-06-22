"""
Custom CBSE PDF Parser
Specialized parser for CBSE test paper format with physics-focused MathJax handling.
"""

import re
from parsers.base_parser import BaseParser

class CustomCBSEPDFParser(BaseParser):
    """
    Custom CBSE parser specialized for CBSE test paper format.
    """
    
    def parse_questions(self, text):
        """
        Parse CBSE test paper format questions.
        
        Args:
            text (str): Text to parse
            
        Returns:
            list: List of parsed questions
        """
        questions = []
        
        # Split text into sections (questions and answers)
        sections = text.split('Answers')
        if len(sections) < 2:
            print("Could not find 'Answers' section in the text")
            return questions
        
        questions_text = sections[0]
        answers_text = sections[1]
        
        # Extract questions
        question_blocks = re.split(r'\n\s*(\d+)\.\s*', questions_text)
        
        for i in range(1, len(question_blocks), 2):  # Skip first empty block, then alternate
            if i + 1 >= len(question_blocks):
                break
                
            question_num = question_blocks[i]
            question_content = question_blocks[i + 1]
            
            if not question_content.strip():
                continue
            
            # Parse the question
            parsed = self.parse_single_question(question_content, question_num)
            if parsed and self.is_valid_question(parsed):
                questions.append(parsed)
        
        # Extract answers and explanations
        answers = self.parse_answers_section(answers_text)
        
        # Merge questions with their answers
        for i, question in enumerate(questions):
            if i < len(answers):
                question.update(answers[i])
        
        return questions
    
    def parse_single_question(self, content, question_num=""):
        """
        Parse a single CBSE question block.
        
        Args:
            content (str): Question content to parse
            question_num (str): Question number
            
        Returns:
            dict: Parsed question dictionary or None if invalid
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        question_text = ""
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        
        current_section = "question"
        
        for line in lines:
            # Skip page numbers
            if re.match(r'^\d+\s*/\s*\d+$', line):
                continue
                
            # Detect question text (lines before options)
            if current_section == "question":
                if re.match(r'^[a-d]\.', line):
                    current_section = "options"
                    option_letter = line[0].upper()
                    option_text = line[2:].strip()
                    options[option_letter] = option_text
                else:
                    question_text += line + " "
                continue
            
            # Handle options
            if current_section == "options":
                if re.match(r'^[a-d]\.', line):
                    option_letter = line[0].upper()
                    option_text = line[2:].strip()
                    options[option_letter] = option_text
                elif any(options.values()):
                    # Continue current option
                    for opt in ['A', 'B', 'C', 'D']:
                        if options[opt] and line.startswith(options[opt][-10:]):  # Check if line continues previous option
                            options[opt] += " " + line
                            break
                    else:
                        # Might be part of question text
                        question_text += line + " "
        
        return self.create_question_dict(
            question_text=question_text,
            options=options,
            question_num=question_num
        )
    
    def parse_answers_section(self, answers_text):
        """
        Parse the answers section to extract answers and explanations.
        
        Args:
            answers_text (str): Text from the answers section
            
        Returns:
            list: List of answer dictionaries
        """
        answers = []
        
        # Split by question numbers
        answer_blocks = re.split(r'\n\s*(\d+)\.\s*', answers_text)
        
        for i in range(1, len(answer_blocks), 2):
            if i + 1 >= len(answer_blocks):
                break
                
            question_num = answer_blocks[i]
            answer_content = answer_blocks[i + 1]
            
            if not answer_content.strip():
                continue
            
            # Extract answer and explanation
            answer_info = self.parse_single_answer(answer_content)
            if answer_info:
                answers.append(answer_info)
        
        return answers
    
    def parse_single_answer(self, content):
        """
        Parse a single answer block.
        
        Args:
            content (str): Answer content to parse
            
        Returns:
            dict: Answer dictionary with 'answer' and 'solution' keys
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        answer = ""
        solution = ""
        
        for line in lines:
            # Skip page numbers
            if re.match(r'^\d+\s*/\s*\d+$', line):
                continue
                
            # Look for answer pattern (e.g., "a.", "b.", "c.", "d.")
            if re.match(r'^[a-d]\.', line):
                answer = line[0].upper()
                solution = line[2:].strip()
            else:
                # Continue explanation
                if solution:
                    solution += " " + line
                else:
                    solution = line
        
        return {
            'answer': answer,
            'solution': solution
        }

def main():
    """
    Main function to run the custom CBSE parser.
    """
    parser = CustomCBSEPDFParser()
    parser.run()

if __name__ == "__main__":
    main() 