import argparse
import os
import json
from pathlib import Path
from file_utils import save_questions_to_json
from llama_cloud_services import LlamaParse

def parse_pdf_with_llama(pdf_path, output_path=None, working_dir=None):

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY") or os.environ.get("LLAMA_API_KEY")
    if not api_key:
        print("Error: Please set the LLAMA_CLOUD_API_KEY or LLAMA_API_KEY environment variable.")
        return

    try:
        # Initialize the parser
        parser = LlamaParse(
            api_key=api_key,
            num_workers=1,  # Single file processing
            verbose=True,
            language="en",
        )

        print(f"Parsing PDF: {pdf_path}")
        
        # Parse the PDF
        result = parser.parse(str(pdf_path))
        
        if output_path:
            # Use the util function for consistency if the result is a list of questions
            try:
                if isinstance(result, list) and all(isinstance(q, dict) for q in result):
                    save_questions_to_json(result, output_path)
                else:
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Parsed result saved to {output_path}")
            except Exception as e:
                print(f"Error saving parsed result: {e}")
        else:
            print(result)
            
        # Optionally, save a log in the working directory
        if working_dir:
            log_path = Path(working_dir) / f"{Path(pdf_path).stem}_llama_parse.log"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(result, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        if working_dir:
            log_path = Path(working_dir) / f"{Path(pdf_path).stem}_llama_parse_error.log"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(str(e))

def main():
    """Main function to run the parser from the command line."""
    parser = argparse.ArgumentParser(description="LlamaParse PDF Parser with interim file support.")
    parser.add_argument('--file', type=str, default=None, help='Process only the specified PDF file (by name or path)')
    args = parser.parse_args()

    input_dir = Path("../input/")
    output_dir = Path("../output/")
    working_dir = Path("../working/")
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)

    try:
        pdf_files = []
        if args.file:
            pdf_path = input_dir / args.file
            if not pdf_path.exists():
                print(f"Error: PDF file not found at {pdf_path}")
                return
            pdf_files = [pdf_path]
        else:
            pdf_files = sorted(input_dir.glob("*.pdf"))
            if not pdf_files:
                print(f"No PDF files found in {input_dir}")
                return
            print(f"Found {len(pdf_files)} PDF file(s) in input directory:")
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf_file.name}")

        for pdf_path in pdf_files:
            output_path = output_dir / f"llama_parsed_{pdf_path.stem}.json"
            print(f"\nProcessing: {pdf_path.name}")
            print("-" * 40)
            parse_pdf_with_llama(str(pdf_path), str(output_path), str(working_dir))
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main() 