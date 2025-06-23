import os
import sys
import json
from pathlib import Path

# --- Django Setup ---
script_path = Path(__file__).resolve()
project_root = script_path.parents[2]
django_project_path = project_root / 'Exam'

if str(django_project_path) not in sys.path:
    sys.path.append(str(django_project_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
import django
django.setup()

from questions.question_models import Question_DB

def load_questions_from_json():
    """
    Loads questions from JSON files in the output directory into the Django database.
    """
    output_dir = project_root / 'question_data_tools' / 'output'

    if not output_dir.exists():
        print(f"Error: Output directory not found at {output_dir}")
        return

    for filename in os.listdir(output_dir):
        if not filename.endswith('.json'):
            continue

        filepath = output_dir / filename
        print(f"Loading questions from: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        for q_data in questions:
            question_type = q_data.get('question_type', '').upper()
            if question_type not in ['MCQ', 'SHORT']:
                continue

            # Prepare parameters for model creation
            params = {
                'question': q_data.get('question', ''),
                'question_type': question_type,
                'solution': q_data.get('solution', ''),
                'max_marks': q_data.get('max_marks', 1),
                'professor': q_data.get('professor', None)
            }

            # Add type-specific fields
            if question_type == 'MCQ':
                params.update({
                    'optionA': q_data.get('optionA', ''),
                    'optionB': q_data.get('optionB', ''),
                    'optionC': q_data.get('optionC', ''),
                    'optionD': q_data.get('optionD', ''),
                    'mcq_answer': q_data.get('mcq_answer', '')
                })
            else:  # SHORT
                params.update({
                    'short_answer': q_data.get('short_answer', '')
                })

            Question_DB.objects.create(**params)
        
        print(f"Successfully loaded {len(questions)} questions from {filename}")

if __name__ == "__main__":
    load_questions_from_json() 