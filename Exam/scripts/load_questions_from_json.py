import os
import sys

# Set up Django environment for standalone script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add project root to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')  # Use your actual settings module
import django
django.setup()

import json
from django.conf import settings
from questions.question_models import Question_DB  # Updated import

# Path to the output JSON files
def get_output_dir():
    # Go one directory up from BASE_DIR
    project_root = os.path.dirname(settings.BASE_DIR)
    return os.path.join(project_root, 'Question Banks', 'question_data_tools', 'output')

def load_questions():
    output_dir = get_output_dir()
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(output_dir, filename)
            print(f"Loading {filepath}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                for q in questions:
                    qtype = q.get('question_type', '').upper()
                    if qtype == 'MCQ':
                        Question_DB.objects.create(
                            question_type='MCQ',
                            question=q.get('question', ''),
                            optionA=q.get('optionA', ''),
                            optionB=q.get('optionB', ''),
                            optionC=q.get('optionC', ''),
                            optionD=q.get('optionD', ''),
                            mcq_answer=q.get('mcq_answer', ''),
                            max_marks=q.get('max_marks', 1),
                            solution=q.get('solution', ''),
                            professor=q.get('professor', None)
                        )
                    elif qtype == 'SHORT':
                        Question_DB.objects.create(
                            question_type='SHORT',
                            question=q.get('question', ''),
                            short_answer=q.get('short_answer', ''),
                            max_marks=q.get('max_marks', 1),
                            solution=q.get('solution', ''),
                            professor=q.get('professor', None)
                        )
            print(f"Loaded {len(questions)} questions from {filename}")

if __name__ == "__main__":
    load_questions() 