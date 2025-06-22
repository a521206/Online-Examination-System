# Question Bank Data Tools

A comprehensive toolkit for extracting and processing questions from PDF files with MathJax equation support.

## 📁 Directory Structure

```
question_data_tools/
├── main.py                 # Main entry point with menu interface
├── README.md               # This documentation file
├── parsers/                # PDF parsing scripts and modules
│   ├── common.py           # Shared functionality and utilities
│   ├── base_parser.py      # Base parser class for inheritance
│   ├── pdf_to_questions.py # Basic PDF parser
│   ├── enhanced_pdf_parser.py # Enhanced PDF parser
│   ├── custom_pdf_parser.py # Custom CBSE parser
│   ├── improved_cbse_parser.py # Improved CBSE parser
│   └── install_pdf_dependencies.py # Dependency installer
├── configs/                # Configuration files
│   └── pdf_requirements.txt
├── input/                  # Input PDF files
│   └── ElectricChargesandFields paper 01.pdf
└── output/                 # Generated output files
    ├── *.json             # Extracted questions
    └── raw_*.txt          # Raw extracted text
```

## 🚀 Quick Start

### 1. Add Your PDF File

Place your PDF file in the `input/` directory:
```bash
# Copy your PDF to the input directory
cp "your_question_paper.pdf" "Question Banks/question_data_tools/input/"
```

### 2. Run the Main Interface

```bash
cd "Question Banks/question_data_tools"
python main.py
```

This will show you a menu with all available tools.

### 3. Install Dependencies

From the main menu, select option `5` to install required dependencies, or run:

```bash
cd parsers
python install_pdf_dependencies.py
```

### 4. Extract Questions

Choose from the available parsers:
- **Basic PDF Parser**: General-purpose PDF extraction
- **Enhanced PDF Parser**: Advanced parsing with better MathJax handling
- **Custom CBSE Parser**: Specialized for CBSE format
- **Improved CBSE Parser**: Enhanced CBSE parsing with better structure detection

## 📋 Available Tools

### Core Modules

1. **Common Module** (`common.py`)
   - Shared PDF extraction functionality
   - MathJax equation conversion
   - Database integration utilities
   - File path management
   - Text cleaning and normalization

2. **Base Parser** (`base_parser.py`)
   - Abstract base class for all parsers
   - Common workflow implementation
   - Standardized question dictionary creation
   - Validation and error handling

### Parsers

1. **Basic PDF Parser** (`pdf_to_questions.py`)
   - General-purpose PDF text extraction
   - Basic question structure detection
   - MathJax equation conversion

2. **Enhanced PDF Parser** (`enhanced_pdf_parser.py`)
   - Advanced text processing
   - Better mathematical expression handling
   - Improved question structure detection

3. **Custom CBSE Parser** (`custom_pdf_parser.py`)
   - Specialized for CBSE test paper format
   - Handles CBSE-specific question and answer structure
   - Physics-focused MathJax conversions

4. **Improved CBSE Parser** (`improved_cbse_parser.py`)
   - Enhanced CBSE format parsing
   - Better text cleaning and normalization
   - Improved answer matching

### Utilities

- **Dependency Installer**: Automatically installs required Python packages

## 🔧 Architecture

### Modular Design

The toolkit uses a modular architecture to eliminate code duplication:

```
BaseParser (abstract)
├── BasicPDFParser
├── EnhancedPDFParser
├── CustomCBSEParser
└── ImprovedCBSEParser
```

### Shared Functionality

All parsers inherit from `BaseParser` and use `common.py` for:
- PDF text extraction (with fallback support)
- MathJax equation conversion
- Database operations
- File I/O operations
- Text cleaning and validation

### Benefits of Refactoring

- **DRY Principle**: No code duplication across parsers
- **Maintainability**: Changes to common functionality affect all parsers
- **Extensibility**: Easy to add new parsers by inheriting from BaseParser
- **Consistency**: All parsers follow the same interface and workflow
- **Testing**: Common functionality can be tested independently

## 📊 Output Files

All extracted data is saved to the `output/` directory:

- `basicpdfparser_questions.json` - Basic parser output
- `enhancedpdfparser_questions.json` - Enhanced parser output
- `customcbseparser_questions.json` - CBSE parser output
- `improvedcbseparser_questions.json` - Improved CBSE parser output
- `raw_*.txt` - Raw extracted text for debugging

## 🔧 Configuration

### Dependencies

Required packages are listed in `configs/pdf_requirements.txt`:
- `PyPDF2>=3.0.0`
- `pdfplumber>=0.9.0`

### PDF File Location

By default, the tools look for PDF files in:
```
input/ElectricChargesandFields paper 01.pdf
```

To use a different PDF file:
1. Place your PDF in the `input/` directory
2. Update the filename in the parser script you want to use
3. Or modify the path in the `main()` function of any parser

## 🎯 Features

### MathJax Support

All parsers automatically convert mathematical expressions to MathJax format:

- **Fractions**: `1/2` → `$\frac{1}{2}$`
- **Subscripts**: `x_1` → `$x_1$`
- **Superscripts**: `x^2` → `$x^2$`
- **Greek letters**: `alpha` → `$\alpha$`
- **Physics symbols**: `∞`, `≤`, `≥`, etc.

### Database Integration

Parsers can directly import questions to your Django database:
- Automatic professor user detection
- Duplicate question prevention
- Error handling and reporting

## 🛠️ Customization

### Adding New Parsers

1. Create a new Python script in the `parsers/` directory
2. Inherit from `BaseParser` class
3. Implement required methods:
   - `parse_questions(text)` - Main parsing logic
   - `parse_single_question(content, question_num)` - Single question parsing
4. Add the parser to the main menu in `main.py`

Example:
```python
from base_parser import BaseParser

class MyCustomParser(BaseParser):
    def parse_questions(self, text):
        # Your parsing logic here
        pass
    
    def parse_single_question(self, content, question_num=""):
        # Your single question parsing logic here
        pass
```

### Modifying MathJax Conversion

Edit the `convert_to_mathjax()` function in `common.py` to:
- Add new mathematical symbols
- Modify conversion patterns
- Adjust LaTeX formatting

### Using Different PDF Files

To process a different PDF file:

1. **Option 1: Replace the default file**
   ```bash
   cp "your_new_paper.pdf" "input/ElectricChargesandFields paper 01.pdf"
   ```

2. **Option 2: Modify the script**
   ```python
   # In any parser script, change this line:
   pdf_path = Path(__file__).parent.parent / "input" / "your_new_paper.pdf"
   ```

## 🐛 Troubleshooting

### Common Issues

1. **No questions found**
   - Check the raw extracted text in `output/raw_*.txt`
   - Verify PDF format matches parser expectations
   - Try a different parser

2. **MathJax not rendering**
   - Ensure equations are wrapped in `$` delimiters
   - Check LaTeX syntax
   - Verify MathJax is configured in your Django templates

3. **Import errors**
   - Ensure professor user exists in database
   - Check question format matches database schema
   - Verify all required fields are present

### Getting Help

1. Check this README file for guidance
2. Review raw extracted text for format issues
3. Try different parsers for your PDF format
4. Customize parsing logic as needed

## 📝 License

This toolkit is part of the Online Examination System project.

## 🤝 Contributing

To add new features or improve existing parsers:

1. Follow the existing code structure and inheritance pattern
2. Add appropriate documentation
3. Test with various PDF formats
4. Update the main menu if adding new tools
5. Ensure new functionality is added to common modules when appropriate 