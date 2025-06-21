#!/usr/bin/env python
"""
Utility script to check and validate the project structure
"""

import os
import sys

def check_directory_structure():
    """Check if the project has the correct directory structure"""
    print("Checking project structure...")
    print("=" * 50)
    
    # Expected directories
    expected_dirs = [
        'tests',
        'utils', 
        'scripts',
        'templates',
        'static',
        'media',
        'data_export',
        'examProject',
        'student',
        'faculty',
        'questions',
        'course',
        'resultprocessing',
        'studentPreferences',
        'tuition'
    ]
    
    # Expected files
    expected_files = [
        'manage.py',
        'README.md',
        'tests/__init__.py',
        'utils/__init__.py', 
        'scripts/__init__.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Check directories
    for dir_name in expected_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (missing)")
            missing_dirs.append(dir_name)
    
    # Check files
    for file_name in expected_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} (missing)")
            missing_files.append(file_name)
    
    # Check test files
    test_files = ['test_passwords.py', 'test_refactored_exam.py', 'test_multiple_attempts.py']
    for test_file in test_files:
        test_path = f"tests/{test_file}"
        if os.path.exists(test_path):
            print(f"✓ {test_path}")
        else:
            print(f"✗ {test_path} (missing)")
            missing_files.append(test_path)
    
    # Check utility files
    util_files = ['fix_passwords.py', 'check_data.py']
    for util_file in util_files:
        util_path = f"utils/{util_file}"
        if os.path.exists(util_path):
            print(f"✓ {util_path}")
        else:
            print(f"✗ {util_path} (missing)")
            missing_files.append(util_path)
    
    # Check script files
    script_files = ['import_data.py', 'export_data.py']
    for script_file in script_files:
        script_path = f"scripts/{script_file}"
        if os.path.exists(script_path):
            print(f"✓ {script_path}")
        else:
            print(f"✗ {script_path} (missing)")
            missing_files.append(script_path)
    
    # Summary
    print(f"\n{'='*50}")
    print("STRUCTURE SUMMARY")
    print(f"{'='*50}")
    
    if not missing_dirs and not missing_files:
        print("🎉 All directories and files are present!")
        return True
    else:
        if missing_dirs:
            print(f"Missing directories: {', '.join(missing_dirs)}")
        if missing_files:
            print(f"Missing files: {', '.join(missing_files)}")
        return False

def check_django_setup():
    """Check if Django is properly set up"""
    print(f"\n{'='*50}")
    print("Checking Django setup...")
    print(f"{'='*50}")
    
    try:
        import django
        print(f"✓ Django version: {django.get_version()}")
        
        # Check if manage.py exists
        if os.path.exists('manage.py'):
            print("✓ manage.py found")
        else:
            print("✗ manage.py not found")
            return False
        
        # Check if settings can be imported
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examProject.settings')
            django.setup()
            print("✓ Django settings loaded successfully")
            return True
        except Exception as e:
            print(f"✗ Error loading Django settings: {e}")
            return False
            
    except ImportError:
        print("✗ Django not installed")
        return False

def main():
    """Main function to run all checks"""
    print("Online Examination System - Structure Check")
    print("=" * 60)
    
    # Check directory structure
    structure_ok = check_directory_structure()
    
    # Check Django setup
    django_ok = check_django_setup()
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    
    if structure_ok and django_ok:
        print("🎉 Project structure is correct and Django is properly set up!")
        print("You can now run the application.")
    else:
        print("⚠️  Some issues were found. Please fix them before proceeding.")
        
        if not structure_ok:
            print("- Check missing directories and files")
        if not django_ok:
            print("- Check Django installation and configuration")

if __name__ == "__main__":
    main() 