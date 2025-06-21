#!/usr/bin/env python
"""
Script to export student and professor data from the database
Run this before recreating the database to preserve important user data
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth.models import User
from faculty.models import FacultyInfo
from student.models import StudentInfo
from studentPreferences.models import StudentPreferenceModel

def export_students():
    """Export student data from student apps"""
    students_data = []
    
    # Export from student.StudentInfo
    try:
        student_info_records = StudentInfo.objects.all()
        for student_info in student_info_records:
            student_data = {
                'model': 'student.StudentInfo',
                'fields': {
                    'user_id': student_info.user.id if student_info.user else None,
                    'address': student_info.address,
                    'picture': str(student_info.picture) if student_info.picture else None,
                }
            }
            students_data.append(student_data)
    except Exception as e:
        print(f"Error exporting student info: {e}")
    
    # Export from studentPreferences
    try:
        student_prefs = StudentPreferenceModel.objects.all()
        for pref in student_prefs:
            student_data = {
                'model': 'studentPreferences.StudentPreferenceModel',
                'fields': {
                    'user_id': pref.user.id if pref.user else None,
                    'sendEmailOnLogin': pref.sendEmailOnLogin,
                }
            }
            students_data.append(student_data)
    except Exception as e:
        print(f"Error exporting student preferences: {e}")
    
    return students_data

def export_professors():
    """Export professor/faculty data"""
    professors_data = []
    
    # Export from faculty.FacultyInfo
    try:
        faculty_records = FacultyInfo.objects.all()
        for faculty in faculty_records:
            professor_data = {
                'model': 'faculty.FacultyInfo',
                'fields': {
                    'user_id': faculty.user.id if faculty.user else None,
                    'address': faculty.address,
                    'subject': faculty.subject,
                    'picture': str(faculty.picture) if faculty.picture else None,
                }
            }
            professors_data.append(professor_data)
    except Exception as e:
        print(f"Error exporting faculty info: {e}")
    
    return professors_data

def export_users():
    """Export User model data for students and professors"""
    users_data = []
    
    try:
        # Get all users that are either students or faculty
        users = User.objects.all()
        for user in users:
            user_data = {
                'model': 'auth.User',
                'fields': {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'password': user.password,  # This is hashed
                    'is_staff': user.is_staff,
                    'is_active': user.is_active,
                    'is_superuser': user.is_superuser,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                }
            }
            users_data.append(user_data)
    except Exception as e:
        print(f"Error exporting users: {e}")
    
    return users_data

def main():
    """Main function to export all data"""
    print("Starting data export...")
    
    # Create export directory
    export_dir = "data_export"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export all data
    all_data = {
        'users': export_users(),
        'students': export_students(),
        'professors': export_professors(),
    }
    
    # Save to JSON file
    export_file = os.path.join(export_dir, f"data_export_{timestamp}.json")
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data export completed!")
    print(f"Export file: {export_file}")
    print(f"Users exported: {len(all_data['users'])}")
    print(f"Students exported: {len(all_data['students'])}")
    print(f"Professors exported: {len(all_data['professors'])}")
    
    # Also create a summary file
    summary_file = os.path.join(export_dir, f"export_summary_{timestamp}.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Data Export Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Users: {len(all_data['users'])}\n")
        f.write(f"Students: {len(all_data['students'])}\n")
        f.write(f"Professors: {len(all_data['professors'])}\n\n")
        f.write("Export completed successfully!\n")
    
    print(f"Summary file: {summary_file}")

if __name__ == "__main__":
    main() 