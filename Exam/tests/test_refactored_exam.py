#!/usr/bin/env python
"""
Test script to verify the refactored exam logic with selected_questions
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth.models import User
from questions.models import Exam_Model
from questions.question_models import Question_DB
from questions.questionpaper_models import Question_Paper
from student.models import StuExamAttempt
import random

def test_refactored_exam_logic():
    """Test the refactored exam logic with selected_questions"""
    
    print("Testing refactored exam logic...")
    print("=" * 50)
    
    # Get a student and exam for testing
    try:
        student = User.objects.get(username='stud1')
        exam = Exam_Model.objects.first()
        
        if not exam:
            print("No exams found in database")
            return
            
        print(f"Testing with student: {student.username}")
        print(f"Testing with exam: {exam.name}")
        print(f"Total questions in exam: {exam.question_paper.questions.count()}")
        
        # Create a test attempt
        attempt = StuExamAttempt.objects.create(
            student=student,
            exam=exam,
            qpaper=exam.question_paper
        )
        
        # Test question selection logic
        all_questions = list(exam.question_paper.questions.all())
        print(f"Available questions: {len(all_questions)}")
        
        if len(all_questions) > 10:
            # Randomly select 10 questions
            random_qs = random.sample(all_questions, 10)
            attempt.selected_questions.set(random_qs)
            attempt.random_qids = ','.join(str(q.qno) for q in random_qs)
        else:
            # Use all questions
            attempt.selected_questions.set(all_questions)
            attempt.random_qids = ','.join(str(q.qno) for q in all_questions)
        
        attempt.save()
        
        # Test the get_selected_questions method
        selected_questions = attempt.get_selected_questions()
        print(f"Selected questions count: {selected_questions.count()}")
        print(f"Selected question IDs: {[q.qno for q in selected_questions]}")
        
        # Verify consistency
        if attempt.selected_questions.count() == selected_questions.count():
            print("✓ selected_questions field and get_selected_questions() are consistent")
        else:
            print("✗ Inconsistency between selected_questions field and get_selected_questions()")
        
        # Test backward compatibility
        if attempt.random_qids:
            qids = [int(qid) for qid in attempt.random_qids.split(',')]
            print(f"Random QIDs from string: {qids}")
            print(f"Questions from QIDs: {[q.qno for q in Question_DB.objects.filter(qno__in=qids)]}")
        
        # Clean up
        attempt.delete()
        print("✓ Test completed successfully")
        
    except User.DoesNotExist:
        print("Student 'stud1' not found. Please run the import script first.")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_refactored_exam_logic() 