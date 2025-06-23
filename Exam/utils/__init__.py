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

openai.api_key = os.getenv("OPENAI_API_KEY")

class ShortAnswerValidationRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: str

class ShortAnswerValidationResult(BaseModel):
    is_correct: bool
    explanation: str


def validate_short_answers_with_llm(requests: List[ShortAnswerValidationRequest]) -> List[ShortAnswerValidationResult]:
    """
    Batch validate short answers using OpenAI LLM. Returns a list of results with correctness and explanation.
    """
    # Compose a single prompt for all questions
    prompt = """
You are an expert exam evaluator. For each question below, compare the student's answer to the correct answer. 
If the student's answer is correct, reply with is_correct: true. If not, reply with is_correct: false and provide a short explanation why, and also provide the correct answer.

Format your response as a JSON list, one object per question, with keys: is_correct (bool), explanation (str).

Questions:
"""
    for i, req in enumerate(requests):
        prompt += f"\nQ{i+1}: {req.question}\nCorrect Answer: {req.correct_answer}\nStudent Answer: {req.student_answer}\n"
    prompt += "\nRespond with only the JSON list."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.0,
    )
    import json
    # Extract the JSON from the LLM response
    content = response["choices"][0]["message"]["content"]
    try:
        data = json.loads(content)
        return [ShortAnswerValidationResult(**item) for item in data]
    except Exception as e:
        # fallback: mark all as incorrect with error explanation
        return [ShortAnswerValidationResult(is_correct=False, explanation=f"LLM error: {e}. Raw: {content}") for _ in requests] 