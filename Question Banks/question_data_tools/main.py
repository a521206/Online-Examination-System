#!/usr/bin/env python3
"""
Main entry point for Question Bank Data Tools
Provides a menu-driven interface to run different PDF parsers and tools.
"""

import os
import sys
from pathlib import Path
from parsers.basic_pdf_parser import BasicPDFParser
from parsers.enhanced_pdf_parser import EnhancedPDFParser
from parsers.custom_cbse_pdf_parser import CustomCBSEPDFParser
from parsers.improved_cbse_pdf_parser import ImprovedCBSEPDFParser

def print_banner():
    print("=" * 60)
    print("           QUESTION BANK DATA TOOLS")
    print("=" * 60)
    print("Extract and process questions from PDF files")
    print("with MathJax equation support")
    print("=" * 60)

def print_menu():
    print("\nAvailable Tools:")
    print("1. Basic PDF Parser (basic_pdf_parser.py)")
    print("2. Enhanced PDF Parser (enhanced_pdf_parser.py)")
    print("3. Custom CBSE Parser (custom_cbse_pdf_parser.py)")
    print("4. Improved CBSE Parser (improved_cbse_pdf_parser.py)")
    print("5. Install Dependencies")
    print("0. Exit")
    print("-" * 60)

def get_pdf_files():
    """Get all PDF files from input directory"""
    input_dir = Path(__file__).parent / "input"
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return []
    
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return []
    
    print(f"Found {len(pdf_files)} PDF file(s) in input directory:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file.name}")
    
    return pdf_files

def run_parser_on_all_files(parser_key):
    """Run parser on all PDF files in input directory"""
    pdf_files = get_pdf_files()
    if not pdf_files:
        return
    
    parsers = {
        'basic': BasicPDFParser,
        'enhanced': EnhancedPDFParser,
        'custom': CustomCBSEPDFParser,
        'improved': ImprovedCBSEPDFParser,
    }
    
    if parser_key not in parsers:
        print(f"Unknown parser: {parser_key}")
        return
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        print("-" * 40)
        try:
            parser = parsers[parser_key](str(pdf_file))
            parser.run()
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

def install_dependencies():
    print("\nInstalling dependencies...")
    print("-" * 40)
    
    try:
        os.chdir(Path(__file__).parent / "parsers")
        os.system("python install_pdf_dependencies.py")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
    finally:
        os.chdir(Path(__file__).parent)

def main():
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("Exiting...")
                break
            elif choice == '1':
                run_parser_on_all_files('basic')
            elif choice == '2':
                run_parser_on_all_files('enhanced')
            elif choice == '3':
                run_parser_on_all_files('custom')
            elif choice == '4':
                run_parser_on_all_files('improved')
            elif choice == '5':
                install_dependencies()
            else:
                print("Invalid choice. Please enter a number between 0 and 5.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 