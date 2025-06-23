"""
LLM utility functions for question parsing, validation, and enrichment using OpenAI.
"""

import json
import re
import openai
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class Question(BaseModel):
    """Pydantic model for a single question (MCQ or Short Answer)."""
    question: str = Field(..., description="The question text, supporting LaTeX for math.")
    question_type: str = Field(..., description="Type of question: 'MCQ' or 'SHORT'.")
    optionA: str = Field(default="", description="Option A for MCQs.")
    optionB: str = Field(default="", description="Option B for MCQs.")
    optionC: str = Field(default="", description="Option C for MCQs.")
    optionD: str = Field(default="", description="Option D for MCQs.")
    mcq_answer: str = Field(default="", description="Correct option for MCQ (A, B, C, or D).")
    short_answer: str = Field(default="", description="Model answer for short answer questions.")
    solution: str = Field(default="", description="Detailed solution or explanation, supporting LaTeX.")
    max_marks: int = Field(default=1, description="Maximum marks for the question.")
    question_num: Optional[str] = Field(default=None, description="Original question number from the source document.")

    @field_validator('question_type')
    @classmethod
    def validate_question_type(cls, v: str) -> str:
        if v.upper() not in ['MCQ', 'SHORT']:
            raise ValueError("question_type must be 'MCQ' or 'SHORT'")
        return v.upper()

    @field_validator('mcq_answer')
    @classmethod
    def validate_mcq_answer(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get('question_type') == 'MCQ' and v and v.upper() not in ['A', 'B', 'C', 'D']:
            raise ValueError('mcq_answer must be A, B, C, or D for an MCQ')
        return v.upper() if v else ''

    @field_validator('question')
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Question text cannot be empty')
        return v.strip()

class Answer(BaseModel):
    """Pydantic model for a single answer, used for combining with questions."""
    question_num: str = Field(..., description="Question number to match with a question.")
    answer: str = Field(..., description="Correct answer, typically a letter for MCQs.")
    solution: str = Field(default="", description="Solution/explanation for the answer.")
    
    @field_validator('answer')
    @classmethod
    def validate_answer_format(cls, v: str) -> str:
        # Flexible answer validation, as it could be a word or letter
        if not v.strip():
            raise ValueError('Answer cannot be empty')
        return v.strip()
    
    @field_validator('question_num')
    @classmethod
    def validate_question_num_format(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Question number cannot be empty')
        return v.strip()

# =============================================================================
# OPENAI API INTERACTION
# =============================================================================

def _call_openai_function_calling(
    prompt: str, 
    system_message: str, 
    function_schema: dict, 
    model: str = "gpt-4-turbo", 
    temperature: float = 0.1, 
    max_tokens: int = 3000
) -> dict:
    """
    Generic function to call OpenAI API with function calling.
    
    Args:
        prompt: The user prompt.
        system_message: The system message to guide the model's behavior.
        function_schema: The schema of the function to be called by the model.
        model: The model to use.
        temperature: The creativity of the response.
        max_tokens: The maximum number of tokens for the response.

    Returns:
        The parsed JSON arguments from the model's function call.
    """
    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            tools=[{"type": "function", "function": function_schema}],
            tool_choice={"type": "function", "function": {"name": function_schema.get("name")}},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls and tool_calls[0].function and tool_calls[0].function.arguments:
            return json.loads(tool_calls[0].function.arguments)
    except Exception as e:
        print(f"An error occurred while calling OpenAI API: {e}")
    return {}

# =============================================================================
# DATA EXTRACTION FUNCTIONS
# =============================================================================

def extract_questions(text: str) -> List[Question]:
    """
    Extracts structured question data from raw text using an LLM.
    """
    system_message = (
        "You are an expert in parsing educational materials. "
        "Your task is to extract all questions (both MCQ and short answer) from the provided text. "
        "Use LaTeX for all mathematical notation."
    )
    
    function_schema = {
        "name": "extract_questions",
        "description": "Extracts MCQ and Short Answer questions from text.",
        "parameters": {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": Question.model_json_schema(ref_template="#/definitions/{model}")
                }
            },
            "required": ["questions"],
            "definitions": {
                "Question": Question.model_json_schema()
            }
        }
    }
    
    prompt = f"Please extract all questions from the following text:\n\n{text}"
    
    response_data = _call_openai_function_calling(prompt, system_message, function_schema)
    
    questions_data = response_data.get("questions", [])
    return [Question(**q) for q in questions_data]

def extract_answers(text: str) -> List[Answer]:
    """
    Extracts structured answer data from raw text using an LLM.
    """
    system_message = (
        "You are an expert in parsing educational materials. "
        "Your task is to extract all answers and their corresponding solutions from an answer key. "
        "Use LaTeX for all mathematical notation."
    )

    function_schema = {
        "name": "extract_answers",
        "description": "Extracts answers and solutions from an answer key.",
        "parameters": {
            "type": "object",
            "properties": {
                "answers": {
                    "type": "array",
                    "items": Answer.model_json_schema(ref_template="#/definitions/{model}")
                }
            },
            "required": ["answers"],
            "definitions": {
                "Answer": Answer.model_json_schema()
            }
        }
    }

    prompt = f"Please extract all answers from the following text:\n\n{text}"
    
    response_data = _call_openai_function_calling(prompt, system_message, function_schema)
    
    answers_data = response_data.get("answers", [])
    return [Answer(**a) for a in answers_data]

# =============================================================================
# DATA PROCESSING AND ENRICHMENT
# =============================================================================

def combine_questions_and_answers(questions: List[Question], answers: List[Answer]) -> List[Question]:
    """
    Merges a list of answers into a list of questions based on question number.
    """
    answer_map = {ans.question_num: ans for ans in answers}
    
    for question in questions:
        if question.question_num and question.question_num in answer_map:
            answer = answer_map[question.question_num]
            if question.question_type == 'MCQ':
                question.mcq_answer = answer.answer
            else: # SHORT
                question.short_answer = answer.answer
            
            if answer.solution:
                question.solution = answer.solution
                
    return questions

def validate_and_enrich_questions(questions: List[Question]) -> List[Question]:
    """
    Validates a list of questions and enriches them using an LLM.
    - Validates the correctness of the question, answer, and options.
    - Generates a concise explanation if it's missing or too short.
    """
    system_message = (
        "You are an expert educational content validator and creator. "
        "For each question provided, please perform the following tasks:\n"
        "1. Validate the question, options, and the provided answer for correctness. If they are incorrect, fix them.\n"
        "2. If the solution is missing or very short (less than 5 words), generate a new, concise explanation (around 20-50 words).\n"
        "3. Ensure all mathematical notation is in proper LaTeX format.\n"
        "Return the validated and enriched list of questions."
    )
    
    function_schema = {
        "name": "validate_and_enrich_questions",
        "description": "Validates and enriches a list of questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": Question.model_json_schema(ref_template="#/definitions/{model}")
                }
            },
            "required": ["questions"],
            "definitions": {
                "Question": Question.model_json_schema()
            }
        }
    }

    # Convert Pydantic objects to a JSON string for the prompt
    questions_json = json.dumps([q.model_dump() for q in questions], indent=2)
    prompt = f"Please validate and enrich the following questions:\n\n{questions_json}"
    
    response_data = _call_openai_function_calling(
        prompt, 
        system_message, 
        function_schema,
        model="gpt-4-turbo",
        temperature=0.0, # Be very precise
        max_tokens=4000
    )
    
    enriched_questions_data = response_data.get("questions", [])
    return [Question(**q) for q in enriched_questions_data]

def generate_solutions_for_questions(questions: List[Question]) -> List[Question]:
    """
    Generates solutions for questions that are missing them.
    This is a more targeted version of the enrichment function.
    """
    # This function can be a lightweight version of validate_and_enrich
    # For now, let's consider it might be needed for a different workflow.
    # We can reuse the logic from `validate_and_enrich_questions` if needed.
    
    questions_to_process = [
        q for q in questions if not q.solution or len(q.solution.split()) < 5
    ]
    
    if not questions_to_process:
        return questions # Return original list if no work to do
    
    print(f"Generating solutions for {len(questions_to_process)} questions.")
    
    # Since this is a subset of the main validation function, we can call it
    enriched_subset = validate_and_enrich_questions(questions_to_process)
    
    # Create a map of the enriched questions for easy updating
    enriched_map = {eq.question: eq for eq in enriched_subset}
    
    # Update the original list with the new solutions
    for i, original_q in enumerate(questions):
        if original_q.question in enriched_map:
            questions[i] = enriched_map[original_q.question]
            
    return questions 