# Question Bank Data Tools

A toolkit for extracting and processing questions from PDF files using OpenAI LLMs, with MathJax equation support.

## 📁 Directory Structure

```
question_data_tools/
├── README.md               # This documentation file
├── requirements.txt        # Python dependencies
├── parsers/                # PDF parsing scripts and modules
│   ├── llm_pdf_parser.py   # LLM-based PDF to questions parser
│   └── llm_utils.py        # LLM prompt, schema, and utility functions
├── input/                  # Input PDF files
│   └── ElectricChargesandFields paper 01.pdf
└── output/                 # Generated output files
    ├── *.json              # Extracted questions
    └── raw_*.txt           # Raw extracted text
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "Question Banks/question_data_tools"
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

You must set your OpenAI API key as an environment variable:

**Linux/macOS:**
```bash
export OPENAI_API_KEY="sk-..."
```
**Windows (cmd):**
```cmd
set OPENAI_API_KEY=sk-...
```
**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
```

### 3. Add Your PDF File

Place your PDF file in the `input/` directory:
```bash
cp "your_question_paper.pdf" "Question Banks/question_data_tools/input/"
```

### 4. Run the LLM PDF Parser

```bash
cd parsers
python llm_pdf_parser.py
```

This will process all PDF files in the `input/` directory and save extracted questions as JSON in the `output/` directory.

## 🧩 Available Tools

- **llm_pdf_parser.py**: Main script for extracting questions from PDFs using OpenAI LLMs.
- **llm_utils.py**: Contains prompt templates, schemas, and utility functions for LLM-based extraction.

## ⚙️ Output Files

All extracted data is saved to the `output/` directory:
- `llm_questions_<filename>.json` - LLM parser output
- `raw_*.txt` - Raw extracted text for debugging

## 📝 Features

- **LLM-based Extraction**: Uses OpenAI's GPT models to intelligently extract both MCQ and Short Answer questions.
- **MathJax Support**: Converts mathematical expressions to MathJax format for compatibility with web and LaTeX renderers.
- **Simple Workflow**: Just drop your PDF in the input folder and run the script.

## 🔑 Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## 🛠️ Customization

- To use a different PDF file, just place it in the `input/` directory. The script will process all PDFs found there.
- Output JSON is compatible with the Django `Question_DB` model (fields: `question_type`, `mcq_answer`, `short_answer`, etc.).

## ❓ FAQ

**Q: How do I add more question types?**
A: Update the prompt and schema in `llm_utils.py` and adjust the transformation logic in `llm_pdf_parser.py`.

**Q: How do I debug extraction issues?**
A: Check the `raw_*.txt` files in the `output/` directory for the raw text extracted from your PDF.

---

For advanced customization, see the code comments in `llm_pdf_parser.py` and `llm_utils.py`. 