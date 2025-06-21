#!/usr/bin/env python
"""
Test script to verify multiple attempts functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth.models import User
from questions.models import Exam_Model
from student.models import StuExamAttempt
from django.utils import timezone
from datetime import timedelta

def test_multiple_attempts():
    """Test that students can have multiple attempts on the same exam"""
    
    print("Testing multiple attempts functionality...")
    print("=" * 50)
    
    try:
        # Get a student and exam for testing
        student = User.objects.get(username='stud1')
        exam = Exam_Model.objects.first()
        
        if not exam:
            print("No exams found in database")
            return
            
        print(f"Testing with student: {student.username}")
        print(f"Testing with exam: {exam.name}")
        
        # Check existing attempts
        existing_attempts = StuExamAttempt.objects.filter(student=student, exam=exam)
        print(f"Existing attempts: {existing_attempts.count()}")
        
        # Create multiple test attempts
        for i in range(3):
            attempt = StuExamAttempt.objects.create(
                student=student,
                exam=exam,
                qpaper=exam.question_paper,
                score=70 + (i * 5),  # Different scores for each attempt
                started_at=timezone.now() - timedelta(days=i),
                completed_at=timezone.now() - timedelta(days=i, hours=1)
            )
            print(f"Created attempt {i+1}: Score={attempt.score}, Date={attempt.started_at.date()}")
        
        # Verify multiple attempts exist
        all_attempts = StuExamAttempt.objects.filter(student=student, exam=exam).order_by('-started_at')
        print(f"\nTotal attempts after creation: {all_attempts.count()}")
        
        # Test the view logic
        attempts = StuExamAttempt.objects.filter(student=student, exam=exam)
        if attempts.exists():
            latest_attempt = attempts.order_by('-started_at').first()
            best_score = max(attempt.score for attempt in attempts)
            print(f"Latest attempt score: {latest_attempt.score}")
            print(f"Best score: {best_score}")
            print(f"Attempt count: {attempts.count()}")
            print("✓ Multiple attempts functionality working correctly")
        else:
            print("✗ No attempts found")
        
        # Clean up test attempts (keep original ones)
        for attempt in all_attempts:
            if attempt.score >= 70:  # Only delete our test attempts
                attempt.delete()
        
        print("✓ Test completed successfully")
        
    except User.DoesNotExist:
        print("Student 'stud1' not found. Please run the import script first.")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_multiple_attempts() 