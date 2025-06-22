"""
Improved CBSE PDF Parser
Enhanced parser for CBSE test paper format with better text cleaning and normalization.
"""

import re
from parsers.base_parser import BaseParser
from parsers.common import clean_text

class ImprovedCBSEPDFParser(BaseParser):
    """
    Improved CBSE parser with enhanced text cleaning and better structure detection.
    """
    
    def parse_questions(self, text):
        """
        Parse CBSE test paper format questions with improved text processing.
        
        Args:
            text (str): Text to parse
            
        Returns:
            list: List of parsed questions
        """
        text = clean_text(text)
        
        questions = []
        
        sections = text.split('Answers')
        if len(sections) < 2:
            print("Could not find 'Answers' section in the text")
            return []
        
        questions_text = sections[0]
        answers_text = sections[1]
        
        question_matches = re.findall(r'(\d+)\.\s*(.*?)(?=\d+\.|$)', questions_text, re.DOTALL)
        
        for question_num, question_content in question_matches:
            parsed = self.parse_single_question(question_content, question_num)
            if parsed and self.is_valid_question(parsed):
                questions.append(parsed)
        
        answers = self.parse_answers_improved(answers_text)
        
        for question in questions:
            question_num = question.get('question_num', '')
            if question_num in answers:
                question.update(answers[question_num])
        
        return questions
    
    def parse_single_question(self, content, question_num=""):
        """
        Parse a single CBSE question block with improved logic.
        
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
        current_option = None
        
        for line in lines:
            if re.match(r'^\d+\s*/\s*\d+$', line) or line in ['CBSE Test Paper-01', 'Class - 12 Physics (Electric Charges and Fields)']:
                continue
            
            if current_section == "question":
                if re.match(r'^[a-d]\.', line):
                    current_section = "options"
                    current_option = line[0].upper()
                    option_text = line[2:].strip()
                    options[current_option] = option_text
                else:
                    question_text += line + " "
                continue
            
            if current_section == "options":
                if re.match(r'^[a-d]\.', line):
                    current_option = line[0].upper()
                    option_text = line[2:].strip()
                    options[current_option] = option_text
                elif current_option and options[current_option]:
                    options[current_option] += " " + line
                else:
                    question_text += line + " "
        
        return self.create_question_dict(
            question_text=question_text,
            options=options,
            question_num=question_num
        )
    
    def parse_answers_improved(self, answers_text):
        """
        Parse the answers section with improved matching.
        
        Args:
            answers_text (str): Text from the answers section
            
        Returns:
            dict: Dictionary mapping question numbers to answer info
        """
        answers = {}
        
        answer_matches = re.findall(r'(\d+)\.\s*(.*?)(?=\d+\.|$)', answers_text, re.DOTALL)
        
        for answer_num, answer_content in answer_matches:
            answer_info = self.parse_single_answer_improved(answer_content)
            if answer_info:
                answers[answer_num] = answer_info
        
        return answers
    
    def parse_single_answer_improved(self, content):
        """
        Parse a single answer block with improved logic.
        
        Args:
            content (str): Answer content to parse
            
        Returns:
            dict: Answer dictionary with 'answer' and 'solution' keys
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        answer = ""
        solution = ""
        
        for line in lines:
            if re.match(r'^\d+\s*/\s*\d+$', line):
                continue
            
            if re.match(r'^[a-d]\.', line):
                answer = line[0].upper()
                solution = line[2:].strip()
            else:
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
    Main function to run the improved CBSE parser.
    """
    parser = ImprovedCBSEPDFParser()
    parser.run()

if __name__ == "__main__":
    main() 