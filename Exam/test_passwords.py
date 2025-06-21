#!/usr/bin/env python
"""
Test script to verify if imported passwords are working correctly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def test_password_authentication():
    """Test if imported users can authenticate with their passwords"""
    
    # Test users with correct passwords
    test_users = [
        {'username': 'stud1', 'password': 'student123'},
        {'username': 'prof1', 'password': 'professor123'},
        {'username': 'agraw', 'password': 'admin123'},
    ]
    
    print("Testing password authentication for imported users...")
    print("=" * 50)
    
    for user_info in test_users:
        username = user_info['username']
        password = user_info['password']
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"✓ User '{username}' exists in database")
            
            # Try to authenticate
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                print(f"✓ Authentication successful for '{username}'")
                print(f"  - User ID: {authenticated_user.id}")
                print(f"  - Email: {authenticated_user.email}")
                print(f"  - Is Staff: {authenticated_user.is_staff}")
                print(f"  - Is Superuser: {authenticated_user.is_superuser}")
            else:
                print(f"✗ Authentication failed for '{username}'")
                
        except User.DoesNotExist:
            print(f"✗ User '{username}' not found in database")
        
        print("-" * 30)

if __name__ == "__main__":
    test_password_authentication() 