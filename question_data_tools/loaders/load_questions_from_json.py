import os
import sys
import json
from pathlib import Path
from django.core.files import File
import logging

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

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_questions_from_json():
    """
    Loads questions from JSON files in the output directory into the Django database.
    """
    output_dir = project_root / 'question_data_tools' / 'output'
    logger.info(f"Starting question loading process from {output_dir}")

    if not output_dir.exists():
        logger.error(f"Error: Output directory not found at {output_dir}")
        return

    for filename in os.listdir(output_dir):
        if not filename.endswith('.json'):
            continue

        filepath = output_dir / filename
        logger.info(f"Processing file: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            logger.info(f"Successfully loaded JSON from {filename} with {len(questions)} questions")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {filename}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error reading {filename}: {e}")
            continue

        for q_index, q_data in enumerate(questions, 1):
            logger.debug(f"Processing question {q_index} from {filename}")
            
            question_type = q_data.get('question_type', '').upper()
            if question_type not in ['MCQ', 'SHORT']:
                logger.warning(f"Skipping question {q_index}: Invalid type '{question_type}'")
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

            try:
                q_obj = Question_DB(**params)
                
                # Handle question image
                if q_data.get('question_image'):
                    img_path = project_root / 'media' / 'question_images' / q_data['question_image']
                    logger.debug(f"Looking for question image at: {img_path}")
                    
                    if img_path.exists():
                        logger.info(f"Found question image: {img_path}")
                        try:
                            with open(img_path, 'rb') as img_file:
                                q_obj.question_image.save(q_data['question_image'], File(img_file), save=False)
                                logger.info(f"Successfully attached question image to question {q_index}")
                        except Exception as e:
                            logger.error(f"Failed to save question image for question {q_index}: {e}")
                    else:
                        logger.warning(f"Question image not found at {img_path}")

                # Handle solution image
                if q_data.get('solution_image'):
                    img_path = project_root / 'media' / 'solution_images' / q_data['solution_image']
                    logger.debug(f"Looking for solution image at: {img_path}")
                    
                    if img_path.exists():
                        logger.info(f"Found solution image: {img_path}")
                        try:
                            with open(img_path, 'rb') as img_file:
                                q_obj.solution_image.save(q_data['solution_image'], File(img_file), save=False)
                                logger.info(f"Successfully attached solution image to question {q_index}")
                        except Exception as e:
                            logger.error(f"Failed to save solution image for question {q_index}: {e}")
                    else:
                        logger.warning(f"Solution image not found at {img_path}")

                q_obj.save()
                logger.info(f"Successfully saved question {q_index} to database")
                
            except Exception as e:
                logger.error(f"Failed to save question {q_index}: {e}")
                continue
        
        logger.info(f"Completed processing {filename}")

if __name__ == "__main__":
    try:
        load_questions_from_json()
    except Exception as e:
        logger.critical(f"Critical error in main execution: {e}") 