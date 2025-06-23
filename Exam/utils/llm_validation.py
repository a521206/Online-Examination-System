import json
from typing import List
from pydantic import BaseModel
from .openai_client import client

class ShortAnswerValidationRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: str
    max_marks: float

class ShortAnswerValidationResult(BaseModel):
    is_correct: bool
    explanation: str
    marks_awarded: float

def validate_short_answers_with_llm(requests: List[ShortAnswerValidationRequest]) -> List[ShortAnswerValidationResult]:
    """
    Batch validate short answers using the OpenAI LLM.

    This function takes a list of validation requests and returns a list of results
    containing correctness, an explanation, and the marks awarded.
    """
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,  # Increased tokens for longer prompts
        temperature=0.0,
    )
    
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return [ShortAnswerValidationResult(**item) for item in data]
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        # Fallback: mark all as incorrect with a detailed error explanation
        error_explanation = f"LLM response parsing failed: {e}. Raw response: {content}"
        return [ShortAnswerValidationResult(is_correct=False, explanation=error_explanation, marks_awarded=0) for _ in requests] 