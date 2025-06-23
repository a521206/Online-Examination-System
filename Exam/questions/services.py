from django.utils import timezone
from student.models import Stu_Question
from utils.llm_validation import ShortAnswerValidationRequest, validate_short_answers_with_llm

def process_exam_submission(attempt, answers):
    """
    Processes the final submission of an exam attempt.

    This service handles creating student answer records, calculating scores for
    MCQs, dispatching short answer questions to an LLM for validation, and
    updating the final score and completion time on the attempt object.
    """
    selected_questions = list(attempt.get_selected_questions())
    
    student_questions_to_create = []
    short_answer_requests = []
    short_answer_map = {}  # Maps LLM request index to the corresponding Stu_Question object

    exam_score = 0.0

    # First pass: Prepare all data and score MCQs
    for ques in selected_questions:
        student_ans = answers.get(str(ques.qno), "")
        
        sq = Stu_Question(
            student=attempt.student,
            question=ques.question,
            optionA=ques.optionA or '',
            optionB=ques.optionB or '',
            optionC=ques.optionC or '',
            optionD=ques.optionD or '',
            answer=ques.mcq_answer if ques.question_type == 'MCQ' else ques.short_answer,
            choice=student_ans,
        )

        if ques.question_type == 'MCQ':
            if student_ans.upper() == (ques.mcq_answer or '').upper():
                sq.marks_awarded = ques.max_marks
                exam_score += ques.max_marks
        elif ques.question_type == 'SHORT':
            short_answer_requests.append(
                ShortAnswerValidationRequest(
                    question=ques.question,
                    correct_answer=ques.short_answer or '',
                    student_answer=student_ans or '',
                    max_marks=ques.max_marks
                )
            )
            short_answer_map[len(short_answer_requests) - 1] = sq
            
        student_questions_to_create.append(sq)

    # Handle short answer validation in a batch
    if short_answer_requests:
        llm_results = validate_short_answers_with_llm(short_answer_requests)
        for i, result in enumerate(llm_results):
            if sq_to_update := short_answer_map.get(i):
                sq_to_update.marks_awarded = result.marks_awarded
                sq_to_update.llm_explanation = result.explanation
                exam_score += result.marks_awarded

    # Bulk create all student questions and finalize the attempt
    attempt.questions.clear()
    created_questions = Stu_Question.objects.bulk_create(student_questions_to_create)
    attempt.questions.add(*created_questions)
    
    attempt.score = exam_score
    attempt.completed_at = timezone.now()
    attempt.save()
    return attempt

def prepare_review_data(attempt):
    """
    Prepares the data required for the exam review page.

    This service fetches the original questions, the student's answers, and
    the LLM feedback, then computes summary statistics for display.
    """
    questions_from_bank = list(attempt.get_selected_questions())
    student_question_map = {sq.question: sq for sq in attempt.questions.all()}
    
    review_data = []
    correct_count = 0
    wrong_count = 0
    not_attempted_count = 0
    total_possible_marks = 0

    for ques_db in questions_from_bank:
        student_question = student_question_map.get(ques_db.question)
        student_ans = student_question.choice if student_question else ""
        
        is_correct = False
        marks_awarded = 0.0
        llm_explanation = ""
        
        if student_question:
            marks_awarded = student_question.marks_awarded
            if ques_db.question_type == 'SHORT':
                llm_explanation = student_question.llm_explanation

        is_correct = marks_awarded == ques_db.max_marks

        review_data.append({
            'question_type': ques_db.question_type,
            'question': ques_db.question,
            'optionA': ques_db.optionA or '',
            'optionB': ques_db.optionB or '',
            'optionC': ques_db.optionC or '',
            'optionD': ques_db.optionD or '',
            'mcq_answer': ques_db.mcq_answer or '',
            'short_answer': ques_db.short_answer or '',
            'student_answer': student_ans,
            'is_correct': is_correct,
            'solution': ques_db.solution or '',
            'marks_awarded': marks_awarded,
            'llm_explanation': llm_explanation,
            'max_marks': ques_db.max_marks,
        })
        
        total_possible_marks += ques_db.max_marks
        
        if not student_ans:
            not_attempted_count += 1
        elif is_correct:
            correct_count += 1
        else:
            wrong_count += 1

    summary = {
        'total_marks': attempt.score,
        'correct': correct_count,
        'wrong': wrong_count,
        'not_attempted': not_attempted_count,
        'total_possible_marks': total_possible_marks
    }
    
    return review_data, summary 