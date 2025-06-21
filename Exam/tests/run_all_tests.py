#!/usr/bin/env python
"""
Script to run all tests in the tests directory
"""

import os
import sys
import subprocess
import importlib.util

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Change to the Exam directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Run the test file
        result = subprocess.run([sys.executable, f"tests/{test_file}"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✓ {test_file} completed successfully")
            return True
        else:
            print(f"✗ {test_file} failed")
            return False
            
    except Exception as e:
        print(f"✗ Error running {test_file}: {e}")
        return False

def main():
    """Run all test files"""
    print("Running all tests for Online Examination System")
    print("=" * 60)
    
    # List of test files to run
    test_files = [
        'test_passwords.py',
        'test_refactored_exam.py', 
        'test_multiple_attempts.py'
    ]
    
    results = []
    for test_file in test_files:
        success = run_test_file(test_file)
        results.append((test_file, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_file, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_file}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

if __name__ == "__main__":
    main() 