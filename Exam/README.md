# Online Examination System

A Django-based online examination system with support for multiple attempts, random question selection, and comprehensive result tracking.

## Project Structure

```
Exam/
├── examProject/          # Main Django project settings
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploaded files
├── data_export/         # Exported data files
├── tests/               # Test scripts
│   ├── __init__.py
│   ├── test_passwords.py
│   ├── test_refactored_exam.py
│   ├── test_multiple_attempts.py
│   └── run_all_tests.py
├── utils/               # Utility scripts
│   ├── __init__.py
│   ├── fix_passwords.py
│   ├── check_data.py
│   └── check_structure.py
├── scripts/             # Data management scripts
│   ├── __init__.py
│   ├── import_data.py
│   └── export_data.py
├── student/             # Student app
├── faculty/             # Faculty app
├── questions/           # Questions and exams app
├── course/              # Course management app
├── resultprocessing/    # Result processing app
├── studentPreferences/  # Student preferences app
└── tuition/             # Tuition management app
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Import Sample Data**:
   ```bash
   python scripts/import_data.py
   ```

4. **Fix Passwords** (if needed):
   ```bash
   python utils/fix_passwords.py
   ```

5. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

## Scripts and Utilities

### Data Management Scripts (`scripts/`)

- **`import_data.py`**: Import student and professor data from JSON exports
  ```bash
  python scripts/import_data.py
  ```

- **`export_data.py`**: Export current data to JSON format
  ```bash
  python scripts/export_data.py
  ```

### Utility Scripts (`utils/`)

- **`fix_passwords.py`**: Fix imported user passwords
  ```bash
  python utils/fix_passwords.py
  ```

- **`check_data.py`**: Validate and check data integrity
  ```bash
  python utils/check_data.py
  ```

- **`check_structure.py`**: Validate project structure and Django setup
  ```bash
  python utils/check_structure.py
  ```

### Test Scripts (`tests/`)

- **`test_passwords.py`**: Test password authentication
  ```bash
  python tests/test_passwords.py
  ```

- **`test_refactored_exam.py`**: Test refactored exam logic
  ```bash
  python tests/test_refactored_exam.py
  ```

- **`test_multiple_attempts.py`**: Test multiple attempts functionality
  ```bash
  python tests/test_multiple_attempts.py
  ```

- **`run_all_tests.py`**: Run all tests at once
  ```bash
  python tests/run_all_tests.py
  ```

## Default Users

After importing data, you can login with:

- **Student**: `stud1` / `student123`
- **Professor**: `prof1` / `professor123`
- **Admin**: `agraw` / `admin123`

## Key Features

### For Students
- Take exams with random question selection
- Multiple attempts on the same exam
- View attempt history and performance
- Review detailed results for each attempt

### For Faculty
- Create and manage exams
- Add questions and question papers
- View student results and attendance
- Upload questions via Excel

### System Features
- Random question selection (10 questions per attempt)
- Session-based answer tracking
- Comprehensive result analysis
- Multiple attempt support
- Data import/export functionality

## Database Models

### Core Models
- **StudentInfo**: Student profile information
- **FacultyInfo**: Faculty profile information
- **Question_DB**: Individual questions
- **Question_Paper**: Question paper collections
- **Exam_Model**: Exam configurations
- **StuExamAttempt**: Student exam attempts
- **Stu_Question**: Student answers

### Key Relationships
- Each exam attempt stores selected random questions
- Students can have multiple attempts per exam
- Questions are linked to professors and question papers
- Results are calculated and stored per attempt

## Development

### Running Tests
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test files
python tests/test_passwords.py
python tests/test_multiple_attempts.py
```

### Data Management
```bash
# Export current data
python scripts/export_data.py

# Import data (after database reset)
python scripts/import_data.py
python utils/fix_passwords.py
```

### Project Validation
```bash
# Check project structure
python utils/check_structure.py

# Check data integrity
python utils/check_data.py
```

### Adding New Features
1. Create migrations for model changes
2. Update views and templates
3. Add tests in `tests/` directory
4. Update documentation

## Troubleshooting

### Common Issues

1. **Password Issues**: Run `python utils/fix_passwords.py`
2. **Missing Data**: Run `python scripts/import_data.py`
3. **Database Issues**: Run `python manage.py migrate`
4. **Structure Issues**: Run `python utils/check_structure.py`

### Logs and Debugging
- Check Django logs in console output
- Use `python utils/check_data.py` for data validation
- Run test scripts to verify functionality
- Use `python utils/check_structure.py` to validate setup

## File Organization

### Tests Directory (`tests/`)
- **Purpose**: All test scripts for validating system functionality
- **Files**: Test scripts for passwords, exam logic, multiple attempts
- **Usage**: Run individual tests or use `run_all_tests.py`

### Utils Directory (`utils/`)
- **Purpose**: Utility scripts for maintenance and validation
- **Files**: Password fixes, data checks, structure validation
- **Usage**: Run as needed for system maintenance

### Scripts Directory (`scripts/`)
- **Purpose**: Data management and import/export operations
- **Files**: Import/export scripts for user data
- **Usage**: Run for data backup and restoration

## Contributing

1. Follow the existing code structure
2. Add tests for new features in `tests/` directory
3. Add utilities in `utils/` directory if needed
4. Add data scripts in `scripts/` directory if needed
5. Update documentation

## License

This project is for educational purposes. 