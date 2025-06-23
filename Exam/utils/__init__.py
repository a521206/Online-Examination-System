"""
Utility scripts for the Online Examination System.

This directory contains utility scripts that help with system maintenance,
data validation, and common operations.
 
Files:
- fix_passwords.py: Script to fix imported user passwords
- check_data.py: Script to check and validate data in the system
""" 

import os
from typing import List
from pydantic import BaseModel
import openai

class ShortAnswerValidationRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: str
    max_marks: float

class ShortAnswerValidationResult(BaseModel):
    is_correct: bool
    explanation: str
    marks_awarded: float


def validate_short_answers_with_llm(requests: List[ShortAnswerValidationRequest], client=None) -> List[ShortAnswerValidationResult]:
    """
    Batch validate short answers using OpenAI LLM. Returns a list of results with correctness, explanation, and marks awarded.
    """
    # Compose a single prompt for all questions
    prompt = """
You are an expert exam evaluator. For each question below, compare the student's answer to the correct answer.
Award marks based on the correctness of the answer. The marks awarded must be a multiple of 0.5 (e.g., 0, 0.5, 1.0, 1.5, ...).

- If the student's answer is fully correct, set 'is_correct' to true and award the full 'max_marks'.
- If the student's answer is partially correct, set 'is_correct' to false, award partial marks (as a multiple of 0.5), and provide a brief explanation.
- If the student's answer is incorrect, set 'is_correct' to false, award 0 marks, and provide a brief explanation.

Format your response as a JSON list, one object per question, with these keys: is_correct (bool), explanation (str), marks_awarded (float).

Questions:
"""
    for i, req in enumerate(requests):
        prompt += f"\nQ{i+1}: {req.question}\nCorrect Answer: {req.correct_answer}\nStudent Answer: {req.student_answer}\nMax Marks: {req.max_marks}\n"
    prompt += "\nRespond with only the JSON list."

    if client is None:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.0,
    )
    import json
    # Extract the JSON from the LLM response
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return [ShortAnswerValidationResult(**item) for item in data]
    except Exception as e:
        # fallback: mark all as incorrect with error explanation
        return [ShortAnswerValidationResult(is_correct=False, explanation=f"LLM error: {e}. Raw: {content}", marks_awarded=0) for _ in requests] 