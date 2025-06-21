#!/usr/bin/env python
"""
Performance test script for the appear_exam view
"""
import os
import sys
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
django.setup()

from django.test import Client
from django.contrib.auth.models import User, Group
from questions.models import Exam_Model
from questions.questionpaper_models import Question_Paper
from questions.question_models import Question_DB

def create_test_data():
    """Create test data for performance testing"""
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        
        # Add to student group
        student_group, _ = Group.objects.get_or_create(name='Student')
        user.groups.add(student_group)
    
    # Create test professor
    prof, created = User.objects.get_or_create(
        username='test_professor',
        defaults={'email': 'prof@example.com'}
    )
    if created:
        prof.set_password('testpass123')
        prof.save()
        
        # Add to professor group
        prof_group, _ = Group.objects.get_or_create(name='Professor')
        prof.groups.add(prof_group)
    
    # Create question paper
    qpaper, created = Question_Paper.objects.get_or_create(
        qPaperTitle='Test Question Paper',
        defaults={'professor': prof}
    )
    
    # Create questions
    for i in range(20):  # Create 20 questions
        question, created = Question_DB.objects.get_or_create(
            question=f'Test Question {i+1}?',
            defaults={
                'professor': prof,
                'optionA': f'Option A for question {i+1}',
                'optionB': f'Option B for question {i+1}',
                'optionC': f'Option C for question {i+1}',
                'optionD': f'Option D for question {i+1}',
                'answer': 'A',
                'max_marks': 10
            }
        )
        if created:
            qpaper.questions.add(question)
    
    # Create exam
    exam, created = Exam_Model.objects.get_or_create(
        name='Performance Test Exam',
        defaults={
            'professor': prof,
            'question_paper': qpaper,
            'total_marks': 100
        }
    )
    
    return user, exam

def test_appear_exam_performance():
    """Test the performance of the appear_exam view"""
    print("Testing appear_exam performance...")
    
    # Create test data
    user, exam = create_test_data()
    
    # Create client
    client = Client()
    
    # Login
    client.login(username='test_student', password='testpass123')
    
    # Test multiple requests
    times = []
    for i in range(5):
        start_time = time.time()
        
        # Make request to appear_exam
        response = client.get(f'/exams/student/appear/{exam.id}/')
        
        end_time = time.time()
        request_time = end_time - start_time
        times.append(request_time)
        
        print(f"Request {i+1}: {request_time:.3f}s - Status: {response.status_code}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nPerformance Summary:")
    print(f"Average time: {avg_time:.3f}s")
    print(f"Min time: {min_time:.3f}s")
    print(f"Max time: {max_time:.3f}s")
    
    # Performance thresholds
    if avg_time < 0.5:
        print("✅ Performance: EXCELLENT")
    elif avg_time < 1.0:
        print("✅ Performance: GOOD")
    elif avg_time < 2.0:
        print("⚠️  Performance: ACCEPTABLE")
    else:
        print("❌ Performance: NEEDS IMPROVEMENT")
    
    return avg_time

if __name__ == '__main__':
    test_appear_exam_performance() 