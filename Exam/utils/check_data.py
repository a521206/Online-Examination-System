#!/usr/bin/env python
"""
Script to check data in the database after import
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth.models import User
from faculty.models import FacultyInfo
from student.models import StudentInfo
from studentPreferences.models import StudentPreferenceModel

def main():
    """Check all data in the database"""
    print("Checking database data...")
    print("=" * 50)
    
    # Check Users
    print(f"\nUsers:")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"  - {user.username} ({user.first_name} {user.last_name}) - {'Staff' if user.is_staff else 'Student'}")
    
    # Check Student data
    print(f"\nStudent Info:")
    student_info = StudentInfo.objects.all()
    print(f"Total student info records: {student_info.count()}")
    for info in student_info:
        print(f"  - User: {info.user.username if info.user else 'None'} - Address: {info.address}")
    
    # Check Student Preferences
    print(f"\nStudent Preferences:")
    student_prefs = StudentPreferenceModel.objects.all()
    print(f"Total student preference records: {student_prefs.count()}")
    for pref in student_prefs:
        print(f"  - User: {pref.user.username if pref.user else 'None'} - Email on login: {pref.sendEmailOnLogin}")
    
    # Check Faculty data
    print(f"\nFaculty Info:")
    faculty_info = FacultyInfo.objects.all()
    print(f"Total faculty info records: {faculty_info.count()}")
    for info in faculty_info:
        print(f"  - User: {info.user.username if info.user else 'None'} - Subject: {info.subject}")
    
    print("\n" + "=" * 50)
    print("Data check completed!")

if __name__ == "__main__":
    main() 