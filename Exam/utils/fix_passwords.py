#!/usr/bin/env python
"""
Script to fix passwords for imported users
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth.models import User

def fix_passwords():
    """Set proper passwords for imported users"""
    
    # Define new passwords for the users
    user_passwords = {
        'stud1': 'student123',
        'prof1': 'professor123', 
        'agraw': 'admin123'
    }
    
    print("Setting passwords for imported users...")
    print("=" * 40)
    
    for username, password in user_passwords.items():
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✓ Set password for '{username}': '{password}'")
        except User.DoesNotExist:
            print(f"✗ User '{username}' not found")
        except Exception as e:
            print(f"✗ Error setting password for '{username}': {e}")
    
    print("\nPassword setup completed!")
    print("\nYou can now login with:")
    print("- Student: stud1 / student123")
    print("- Professor: prof1 / professor123") 
    print("- Admin: agraw / admin123")

if __name__ == "__main__":
    fix_passwords() 