#!/usr/bin/env python
"""
Script to import student and professor data back to the database
Run this after recreating the database to restore important user data
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

def import_users(users_data):
    """Import User model data"""
    imported_count = 0
    for user_data in users_data:
        try:
            fields = user_data['fields']
            
            # Create user
            user = User.objects.create_user(
                username=fields['username'],
                email=fields['email'],
                password=fields['password'],  # This should be the hashed password
                first_name=fields['first_name'],
                last_name=fields['last_name'],
                is_staff=fields['is_staff'],
                is_active=fields['is_active'],
                is_superuser=fields['is_superuser'],
            )
            
            # Set date fields
            if fields['date_joined']:
                user.date_joined = datetime.fromisoformat(fields['date_joined'])
            if fields['last_login']:
                user.last_login = datetime.fromisoformat(fields['last_login'])
            user.save()
            
            imported_count += 1
            print(f"Imported user: {user.username}")
            
        except Exception as e:
            print(f"Error importing user {fields.get('username', 'unknown')}: {e}")
    
    return imported_count

def import_students(students_data):
    """Import student data"""
    imported_count = 0
    for student_data in students_data:
        try:
            model_name = student_data['model']
            fields = student_data['fields']
            
            if model_name == 'student.StudentInfo':
                # Import StudentInfo
                user = User.objects.get(id=fields['user_id']) if fields['user_id'] else None
                student_info = StudentInfo.objects.create(
                    user=user,
                    address=fields['address'],
                    picture=fields['picture'] if fields['picture'] != 'None' else None,
                )
                imported_count += 1
                print(f"Imported StudentInfo for user: {user.username if user else 'None'}")
                
            elif model_name == 'studentPreferences.StudentPreferenceModel':
                # Import StudentPreferenceModel
                user = User.objects.get(id=fields['user_id']) if fields['user_id'] else None
                student_pref = StudentPreferenceModel.objects.create(
                    user=user,
                    sendEmailOnLogin=fields['sendEmailOnLogin'],
                )
                imported_count += 1
                print(f"Imported StudentPreference for user: {user.username if user else 'None'}")
                
        except Exception as e:
            print(f"Error importing student data: {e}")
    
    return imported_count

def import_professors(professors_data):
    """Import professor/faculty data"""
    imported_count = 0
    for professor_data in professors_data:
        try:
            fields = professor_data['fields']
            
            # Import FacultyInfo
            user = User.objects.get(id=fields['user_id']) if fields['user_id'] else None
            faculty_info = FacultyInfo.objects.create(
                user=user,
                address=fields['address'],
                subject=fields['subject'],
                picture=fields['picture'] if fields['picture'] != 'None' else None,
            )
            imported_count += 1
            print(f"Imported FacultyInfo for user: {user.username if user else 'None'}")
            
        except Exception as e:
            print(f"Error importing faculty data: {e}")
    
    return imported_count

def main():
    """Main function to import all data"""
    print("Starting data import...")
    
    # Find the most recent export file
    export_dir = "data_export"
    if not os.path.exists(export_dir):
        print("No export directory found!")
        return
    
    export_files = [f for f in os.listdir(export_dir) if f.startswith('data_export_') and f.endswith('.json')]
    if not export_files:
        print("No export files found!")
        return
    
    # Get the most recent file
    latest_file = max(export_files)
    export_file = os.path.join(export_dir, latest_file)
    
    print(f"Importing from: {export_file}")
    
    # Load data
    with open(export_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    # Import data
    users_imported = import_users(all_data.get('users', []))
    students_imported = import_students(all_data.get('students', []))
    professors_imported = import_professors(all_data.get('professors', []))
    
    print(f"\nImport completed!")
    print(f"Users imported: {users_imported}")
    print(f"Students imported: {students_imported}")
    print(f"Professors imported: {professors_imported}")

if __name__ == "__main__":
    main() 