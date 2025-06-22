import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from questions.question_models import Question_DB

class Command(BaseCommand):
    help = 'Load questions from JSON files in the output directory'

    def handle(self, *args, **options):
        # Go one directory up from BASE_DIR
        project_root = os.path.dirname(settings.BASE_DIR)
        self.stdout.write(f"project_root: {project_root}")
        output_dir = os.path.join(project_root, 'Question Banks', 'question_data_tools', 'output')
        self.stdout.write(f"output_dir: {output_dir}")
        
        if not os.path.exists(output_dir):
            self.stdout.write(
                self.style.ERROR(f'Output directory not found: {output_dir}')
            )
            return
        
        total_loaded = 0
        
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(output_dir, filename)
                self.stdout.write(f"Loading {filepath}...")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        questions = json.load(f)
                        
                        for q in questions:
                            # Create question object
                            if q['question_type'].upper() == 'MCQ':
                                question = Question_DB(
                                    question_type='MCQ',
                                    question=q['question'],
                                    optionA=q.get('optionA', ''),
                                    optionB=q.get('optionB', ''),
                                    optionC=q.get('optionC', ''),
                                    optionD=q.get('optionD', ''),
                                    mcq_answer=q.get('mcq_answer', ''),
                                    max_marks=q.get('max_marks', 1),
                                    solution=q.get('solution', ''),
                                    professor=q.get('professor', '')
                                )
                            elif q['question_type'].upper() == 'SHORT':
                                question = Question_DB(
                                    question_type='SHORT',
                                    question=q['question'],
                                    short_answer=q.get('short_answer', ''),
                                    max_marks=q.get('max_marks', 1),
                                    solution=q.get('solution', ''),
                                    professor=q.get('professor', '')
                                )
                            question.save()
                            total_loaded += 1
                            
                    self.stdout.write(
                        self.style.SUCCESS(f"Loaded {len(questions)} questions from {filename}")
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error loading {filename}: {str(e)}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"Total questions loaded: {total_loaded}")
        ) 