"""
LLM utility functions for question parsing and validation.
"""

import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import openai

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class Question(BaseModel):
    """Pydantic model for question structure."""
    question: str = Field(..., description="The question text")
    optionA: str = Field(default="", description="Option A")
    optionB: str = Field(default="", description="Option B")
    optionC: str = Field(default="", description="Option C")
    optionD: str = Field(default="", description="Option D")
    answer: str = Field(default="", description="Correct answer (A, B, C, or D)")
    solution: str = Field(default="", description="Solution/explanation")
    max_marks: int = Field(default=1, description="Maximum marks for the question")
    question_num: Optional[str] = Field(default=None, description="Question number")
    
    @field_validator('answer')
    @classmethod
    def validate_answer(cls, v):
        if v and v.upper() not in ['A', 'B', 'C', 'D']:
            raise ValueError('Answer must be A, B, C, or D')
        return v.upper()
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question text cannot be empty')
        return v.strip()
    
    def is_valid(self) -> bool:
        """Check if question has at least one option."""
        options = [self.optionA, self.optionB, self.optionC, self.optionD]
        return any(opt.strip() for opt in options)

class Answer(BaseModel):
    """Pydantic model for answer structure."""
    question_num: str = Field(..., description="Question number")
    answer: str = Field(..., description="Correct answer (A, B, C, or D)")
    solution: str = Field(default="", description="Solution/explanation")
    
    @field_validator('answer')
    @classmethod
    def validate_answer(cls, v):
        if v and v.upper() not in ['A', 'B', 'C', 'D']:
            raise ValueError('Answer must be A, B, C, or D')
        return v.upper()
    
    @field_validator('question_num')
    @classmethod
    def validate_question_num(cls, v):
        if not v.strip():
            raise ValueError('Question number cannot be empty')
        return v.strip()

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def create_questions_prompt(questions_text: str) -> str:
    """Create prompt for extracting questions."""
    return f"""
You are an expert at extracting multiple choice questions (MCQs) from educational text. 

Extract all well-formed MCQs from the following text and return them as a JSON array. 
Each question must have:
- "question": The question text (use LaTeX for all math, wrap inline math in $...$)
- "optionA", "optionB", "optionC", "optionD": Four answer options (use LaTeX for math)
- "answer": Leave empty for now
- "solution": Leave empty for now
- "max_marks": 1
- "question_num": Question number if available, else empty string

IMPORTANT:
- Use LaTeX for all mathematical expressions.
- Only include questions with at least 3 options.
- Skip incomplete, ambiguous, or non-MCQ content.
- Return only a valid JSON array, no extra text.
- There are approximately 15 questions in this document - extract all of them.
- Focus only on extracting the question structure, leave answers empty.

Example output:
[
  {{
    "question": "What is the value of $2^3$?",
    "optionA": "4",
    "optionB": "6",
    "optionC": "8",
    "optionD": "16",
    "answer": "",
    "solution": "",
    "max_marks": 1,
    "question_num": "1"
  }}
]

QUESTIONS SECTION:
{questions_text}
"""

def create_answers_prompt(answers_text: str) -> str:
    """Create prompt for extracting answers."""
    return f"""
You are an expert at extracting answers and solutions from educational answer keys.

Extract all answers and solutions from the following text and return them as a JSON array.
Each answer must have:
- "question_num": The question number
- "answer": The correct option ("A", "B", "C", or "D")
- "solution": Solution/explanation (use LaTeX for math, or empty string if not available)

IMPORTANT:
- Use LaTeX for all mathematical expressions.
- Match question numbers exactly.
- Extract all answers present in the text.
- Return only a valid JSON array, no extra text.
- Use LaTeX for mathematical expressions in solutions.

Example output:
[
  {{
    "question_num": "1",
    "answer": "C",
    "solution": "Because $2^3 = 2 \\times 2 \\times 2 = 8$"
  }}
]

ANSWERS SECTION:
{answers_text}
"""

# =============================================================================
# FUNCTION SCHEMAS FOR OPENAI FUNCTION CALLING
# =============================================================================

question_function_schema = {
    "name": "extract_questions",
    "description": "Extracts MCQ questions from text in a structured format.",
    "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "optionA": {"type": "string"},
                        "optionB": {"type": "string"},
                        "optionC": {"type": "string"},
                        "optionD": {"type": "string"},
                        "answer": {"type": "string"},
                        "solution": {"type": "string"},
                        "max_marks": {"type": "integer", "default": 1},
                        "question_num": {"type": "string"},
                    },
                    "required": ["question", "optionA", "optionB", "optionC", "optionD"]
                }
            }
        },
        "required": ["questions"]
    }
}

answer_function_schema = {
    "name": "extract_answers",
    "description": "Extracts MCQ answers and solutions from text in a structured format.",
    "parameters": {
        "type": "object",
        "properties": {
            "answers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_num": {"type": "string"},
                        "answer": {"type": "string"},
                        "solution": {"type": "string"},
                    },
                    "required": ["question_num", "answer"]
                }
            }
        },
        "required": ["answers"]
    }
}

# =============================================================================
# LLM API CALLS
# =============================================================================

def call_openai_function_call(prompt: str, system_message: str, function_schema: dict, function_name: str, max_tokens: int = 2000) -> dict:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        tools=[{"type": "function", "function": function_schema}],
        tool_choice={"type": "function", "function": {"name": function_name}},
        max_tokens=max_tokens,
        temperature=0.1
    )
    # Parse tool_calls
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls and tool_calls[0].function and tool_calls[0].function.arguments:
        return json.loads(tool_calls[0].function.arguments)
    return {}

def extract_questions(questions_text: str) -> List[Question]:
    prompt = create_questions_prompt(questions_text)
    system_message = "Extract educational questions as JSON with exact structure"
    result = call_openai_function_call(prompt, system_message, question_function_schema, "extract_questions", max_tokens=4000)
    questions = result.get("questions", [])
    return [Question(**q) for q in questions if isinstance(q, dict)]

def extract_answers(answers_text: str) -> List[Answer]:
    prompt = create_answers_prompt(answers_text)
    system_message = "Extract answers and solutions as JSON with exact structure"
    result = call_openai_function_call(prompt, system_message, answer_function_schema, "extract_answers", max_tokens=4000)
    answers = result.get("answers", [])
    return [Answer(**a) for a in answers if isinstance(a, dict)]

# =============================================================================
# MAIN PROCESSING FUNCTION
# =============================================================================

def call_openai_api_main(questions_text: str, answers_text: str = "") -> List[Question]:
    """Main function: Extract questions first, then answers, then combine."""
    print("Step 1: Extracting questions...")
    questions = extract_questions(questions_text)
    
    if not answers_text:
        print("No answers section found, returning questions without answers.")
        return questions
    
    print("Step 2: Extracting answers...")
    answers = extract_answers(answers_text)
    
    print("Step 3: Combining questions and answers...")
    return combine_questions_and_answers(questions, answers)

# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def parse_questions_response(response: str) -> List[Question]:
    """Parse JSON response for questions."""
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            raw_questions = json.loads(json_match.group())
            valid_questions = []
            
            for raw_q in raw_questions:
                try:
                    question = Question(**raw_q)
                    if question.is_valid():
                        valid_questions.append(question)
                except:
                    continue
            
            return valid_questions
        return []
    except:
        return []

def parse_answers_response(response: str) -> List[Answer]:
    """Parse JSON response for answers."""
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            raw_answers = json.loads(json_match.group())
            valid_answers = []
            
            for raw_a in raw_answers:
                try:
                    answer = Answer(**raw_a)
                    valid_answers.append(answer)
                except:
                    continue
            
            return valid_answers
        return []
    except:
        return []

# =============================================================================
# COMBINATION FUNCTION
# =============================================================================

def combine_questions_and_answers(questions: List[Question], answers: List[Answer]) -> List[Question]:
    """Combine questions with their corresponding answers."""
    # Create a dictionary of answers by question number
    answers_dict = {answer.question_num: answer for answer in answers}
    
    # Update questions with answers
    for question in questions:
        if question.question_num in answers_dict:
            answer = answers_dict[question.question_num]
            question.answer = answer.answer
            question.solution = answer.solution
    
    return questions 