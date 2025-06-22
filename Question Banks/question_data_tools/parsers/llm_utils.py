"""
LLM utility functions for question parsing and validation.
"""

import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import openai

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

def call_openai_api(questions_text: str, answers_text: str = "") -> List[Question]:
    """Call OpenAI API to parse questions from text."""
    # Build the prompt with both questions and answers
    if answers_text:
        prompt = f"""
You are an expert at extracting multiple choice questions (MCQs) from educational text. 

Extract all well-formed MCQs from the following text and return them as a JSON array. 
Each question must have:
- "question": The question text (use LaTeX for all math, wrap inline math in $...$)
- "optionA", "optionB", "optionC", "optionD": Four answer options (use LaTeX for math)
- "answer": The correct option ("A", "B", "C", or "D") if available, else empty string
- "solution": Solution/explanation (use LaTeX for math, or empty string if not available)
- "max_marks": 1
- "question_num": Question number if available, else empty string

IMPORTANT:
- Use LaTeX for all mathematical expressions.
- Only include questions with at least 3 options.
- Skip incomplete, ambiguous, or non-MCQ content.
- Return only a valid JSON array, no extra text.
- Use the answers section to fill in correct answers and solutions.
- Explanations found in the answers section should be used as the "solution" field.
- Match question numbers with answer numbers to ensure correct answer mapping.
- There are approximately 15 questions in this document - extract all of them.

Example output:
[
  {{
    "question": "What is the value of $2^3$?",
    "optionA": "4",
    "optionB": "6",
    "optionC": "8",
    "optionD": "16",
    "answer": "C",
    "solution": "Because $2^3 = 2 \\times 2 \\times 2 = 8$",
    "max_marks": 1,
    "question_num": "1"
  }}
]

QUESTIONS SECTION:
{questions_text}

ANSWERS SECTION:
{answers_text}
"""
    else:
        prompt = f"""
You are an expert at extracting multiple choice questions (MCQs) from educational text. 

Extract all well-formed MCQs from the following text and return them as a JSON array. 
Each question must have:
- "question": The question text (use LaTeX for all math, wrap inline math in $...$)
- "optionA", "optionB", "optionC", "optionD": Four answer options (use LaTeX for math)
- "answer": The correct option ("A", "B", "C", or "D") if available, else empty string
- "solution": Solution/explanation (use LaTeX for math, or empty string if not available)
- "max_marks": 1
- "question_num": Question number if available, else empty string

IMPORTANT:
- Use LaTeX for all mathematical expressions.
- Only include questions with at least 3 options.
- Skip incomplete, ambiguous, or non-MCQ content.
- Return only a valid JSON array, no extra text.
- Use the answers section to fill in correct answers and solutions.
- Explanations found in the answers section should be used as the "solution" field.
- Match question numbers with answer numbers to ensure correct answer mapping.
- There are approximately 15 questions in this document - extract all of them.

Example output:
[
  {{
    "question": "What is the value of $2^3$?",
    "optionA": "4",
    "optionB": "6",
    "optionC": "8",
    "optionD": "16",
    "answer": "C",
    "solution": "Because $2^3 = 2 \\times 2 \\times 2 = 8$",
    "max_marks": 1,
    "question_num": "1"
  }}
]

Text to process:
{questions_text}
"""
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract educational questions as JSON with exact structure"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.1
    )
    content = response.choices[0].message.content.strip()
    return parse_json_response(content)

def parse_json_response(response: str) -> List[Question]:
    """Parse JSON response from OpenAI and validate with Pydantic."""
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