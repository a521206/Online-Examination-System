#!/usr/bin/env python3
"""
Script to install PDF processing dependencies for the question extraction system.
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    print("Installing PDF processing dependencies...")
    print("=" * 50)
    
    packages = [
        "pdfplumber>=0.9.0",
        "PyPDF2>=3.0.0"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 50)
    print(f"Installation complete: {success_count}/{len(packages)} packages installed successfully.")
    
    if success_count == len(packages):
        print("\nYou can now run the PDF extraction scripts:")
        print("  python scripts/pdf_to_questions.py")
        print("  python scripts/enhanced_pdf_parser.py")
    else:
        print("\nSome packages failed to install. Please install them manually:")
        for package in packages:
            print(f"  pip install {package}")

if __name__ == "__main__":
    main() 