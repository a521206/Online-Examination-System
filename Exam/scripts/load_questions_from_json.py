import os
import json
from django.conf import settings
from questions.models import Question  # Adjust import as needed

# Path to the output JSON files
def get_output_dir():
    return os.path.join(settings.BASE_DIR, 'Question Banks', 'question_data_tools', 'output')

def load_questions():
    output_dir = get_output_dir()
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(output_dir, filename)
            print(f"Loading {filepath}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                for q in questions:
                    # Adjust field mapping as per your Question model
                    Question.objects.create(
                        question_text=q.get('question', ''),
                        optionA=q.get('optionA', ''),
                        optionB=q.get('optionB', ''),
                        optionC=q.get('optionC', ''),
                        optionD=q.get('optionD', ''),
                        answer=q.get('answer', ''),
                        solution=q.get('solution', ''),
                        max_marks=q.get('max_marks', 1),
                        question_num=q.get('question_num', ''),
                    )
            print(f"Loaded {len(questions)} questions from {filename}")

if __name__ == "__main__":
    load_questions() 