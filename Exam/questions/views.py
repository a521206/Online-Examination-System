from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.models import Group
from student.models import *
from django.utils import timezone
from questions.questionpaper_models import QPForm
from questions.question_models import QForm, Question_DB
from questions.models import ExamForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.contrib import messages
import pandas as pd
from django.core.files.storage import FileSystemStorage
import json
import io
import base64
from django.core.paginator import Paginator
import random
from utils.performance_monitor import monitor_performance
import time
from utils import validate_short_answers_with_llm, ShortAnswerValidationRequest
import openai
import os

def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@login_required(login_url='faculty-login')
def view_exams_prof(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = ExamForm(prof_user)
        if request.method == 'POST' and permissions:
            form = ExamForm(prof_user,request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof
                exam.save()
                form.save_m2m()
                return redirect('view_exams')

        exams = Exam_Model.objects.filter(professor=prof)
        return render(request, 'exam/mainexam.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def add_question_paper(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = QPForm(prof_user)
        if request.method == 'POST' and permissions:
            form = QPForm(prof_user,request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof_user
                exam.save()
                form.save_m2m()
                return redirect('faculty-add_question_paper')

        exams = Exam_Model.objects.filter(professor=prof)
        return render(request, 'exam/addquestionpaper.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def add_questions(request):
    prof = request.user
    prof_user = User.objects.get(username=prof)
    permissions = False
    if prof:
        permissions = has_group(prof,"Professor")
    if permissions:
        new_Form = QForm()
        if request.method == 'POST' and permissions:
            form = QForm(request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                exam.professor = prof_user
                exam.save()
                form.save_m2m()
                return redirect('faculty-addquestions')

        exams = Exam_Model.objects.filter(professor=prof)
        return render(request, 'exam/addquestions.html', {
            'exams': exams, 'examform': new_Form, 'prof': prof,
        })
    else:
        return redirect('view_exams_student')

@login_required(login_url='faculty-login')
def view_previousexams_prof(request):
    prof = request.user
    student = 0
    exams = Exam_Model.objects.filter(professor=prof)
    return render(request, 'exam/previousexam.html', {
        'exams': exams,'prof': prof
    })

@login_required(login_url='login')
def student_view_previous(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    list_un = []
    exam_attempts_map = {}
    from student.models import StuExamAttempt
    
    for exam in exams:
        attempts = StuExamAttempt.objects.filter(student=request.user, exam=exam).order_by('-started_at')
        if attempts.exists():
            list_of_completed.append(exam)
            exam_attempts_map[exam.id] = attempts
        else:
            list_un.append(exam)
    
    # Attach attempts to each exam for template
    for exam in list_of_completed:
        exam.attempts = exam_attempts_map.get(exam.id, [])
    
    # Calculate statistics
    total_exams = len(list_of_completed)
    total_attempts = sum(len(attempts) for attempts in exam_attempts_map.values())
    
    # Calculate average score
    total_score = 0
    total_count = 0
    last_attempt_date = None
    
    for attempts in exam_attempts_map.values():
        for attempt in attempts:
            total_score += attempt.score
            total_count += 1
            if last_attempt_date is None or attempt.started_at > last_attempt_date:
                last_attempt_date = attempt.started_at
    
    average_score = round(total_score / total_count, 1) if total_count > 0 else 0
    
    return render(request, 'exam/previousstudent.html', {
        'exams': list_un,
        'completed': list_of_completed,
        'total_exams': total_exams,
        'total_attempts': total_attempts,
        'average_score': average_score,
        'last_attempt_date': last_attempt_date
    })

@login_required(login_url='faculty-login')
def view_students_prof(request):
    students = User.objects.filter(groups__name = "Student")
    student_name = []
    student_completed = []
    count = 0
    dicts = {}
    examn = Exam_Model.objects.filter(professor=request.user)
    for student in students:
        student_name.append(student.username)
        count = 0
        for exam in examn:
            if StuExamAttempt.objects.filter(student=student, exam=exam).exists():
                count += 1
            else:
                count += 0
        student_completed.append(count)
    i = 0
    for x in student_name:
        dicts[x] = student_completed[i]
        i+=1
    return render(request, 'exam/viewstudents.html', {
        'students':dicts
    })

@login_required(login_url='faculty-login')
def view_results_prof(request):
    students = User.objects.filter(groups__name = "Student")
    dicts = {}
    prof = request.user
    professor = User.objects.get(username=prof.username)
    examn = Exam_Model.objects.filter(professor=professor)
    for exam in examn:
        attempts = StuExamAttempt.objects.filter(exam=exam)
        for attempt in attempts:
            key = f"{attempt.student.username} {attempt.exam.name} {attempt.qpaper.qPaperTitle}"
            dicts[key] = attempt.score
    return render(request, 'exam/resultsstudent.html', {
        'students':dicts
    })

@login_required(login_url='login')
def view_exams_student(request):
    exams = Exam_Model.objects.all()
    available_exams = []
    completed_exams = []
    
    for exam in exams:
        attempts = StuExamAttempt.objects.filter(student=request.user, exam=exam)
        if attempts.exists():
            # Student has attempted this exam before
            latest_attempt = attempts.order_by('-started_at').first()
            completed_exams.append({
                'exam': exam,
                'attempt_count': attempts.count(),
                'latest_score': latest_attempt.score,
                'latest_attempt_date': latest_attempt.completed_at,
                'best_score': max(attempt.score for attempt in attempts)
            })
        else:
            # Student hasn't attempted this exam yet
            available_exams.append(exam)

    return render(request,'exam/mainexamstudent.html',{
        'available_exams': available_exams,
        'completed_exams': completed_exams
    })

@login_required(login_url='login')
def view_students_attendance(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    list_un = []
    for exam in exams:
        if StuExamAttempt.objects.filter(student=request.user, exam=exam).exists():
            list_of_completed.append(exam)
        else:
            list_un.append(exam)

    return render(request,'exam/attendance.html',{
        'exams':list_un,
        'completed':list_of_completed
    })

def convert(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60) 
    min += hour*60
    return "%02d:%02d" % (min, sec) 

@monitor_performance("appear_exam")
@login_required(login_url='login')
def appear_exam(request, id):
    start_time = time.time()
    
    student = request.user
    from .question_models import Question_DB
    QUESTIONS_PER_PAGE = 5
    
    if request.method == 'GET':
        # Optimize database queries with select_related and prefetch_related
        exam = Exam_Model.objects.select_related('question_paper', 'professor').get(pk=id)
        
        # Create a new attempt for each exam start
        attempt_id = request.session.get(f'exam_{exam.id}_attempt_id')
        attempt = None
        now = timezone.now()
        if attempt_id:
            try:
                attempt = StuExamAttempt.objects.select_related('exam', 'qpaper').prefetch_related('selected_questions').get(
                    id=attempt_id, student=student, exam=exam
                )
                # If the attempt is completed or expired, ignore it and create a new one
                if attempt.completed_at or (attempt.end_time and now >= attempt.end_time):
                    attempt = None
                    del request.session[f'exam_{exam.id}_attempt_id']
            except StuExamAttempt.DoesNotExist:
                attempt = None
        
        if not attempt:
            # Create new attempt with explicit started_at
            attempt = StuExamAttempt.objects.create(
                student=student, 
                exam=exam, 
                qpaper=exam.question_paper,
                started_at=timezone.now()
            )
            request.session[f'exam_{exam.id}_attempt_id'] = attempt.id
            
            # Optimize question selection - use database-level random selection
            all_questions = exam.question_paper.questions.all()
            question_count = all_questions.count()
            
            if question_count > 10:
                # Use database-level random selection for better performance
                from django.db.models import Q
                import random
                
                # Get random question IDs efficiently
                all_qids = list(all_questions.values_list('qno', flat=True))
                if len(all_qids) > 10:
                    random_qids = random.sample(all_qids, 10)
                    random_qs = Question_DB.objects.filter(qno__in=random_qids)
                else:
                    random_qs = all_questions
                
                # Store the selected questions directly in the attempt
                attempt.selected_questions.set(random_qs)
                # Also store IDs for backward compatibility
                attempt.random_qids = ','.join(str(q.qno) for q in random_qs)
            else:
                # If 10 or fewer questions, use all questions
                attempt.selected_questions.set(all_questions)
                attempt.random_qids = ','.join(str(q.qno) for q in all_questions)
            attempt.save()
        
        # Get the questions selected for this attempt - optimize with prefetch
        selected_questions = list(attempt.selected_questions.all().order_by('qno'))
        
        paginator = Paginator(selected_questions, QUESTIONS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        answers = request.session.get(f'exam_{exam.id}_answers', {})
        
        # Calculate starting question number for this page
        start_question_number = (page_obj.number - 1) * QUESTIONS_PER_PAGE + 1
        
        # Calculate remaining time based on attempt's end_time
        if attempt.end_time and now < attempt.end_time:
            time_remaining = attempt.end_time - now
            total_seconds = int(time_remaining.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
        else:
            # If attempt time has expired, redirect to time expired page
            if attempt.end_time and now >= attempt.end_time:
                # Auto-submit the exam if not already completed
                if not attempt.completed_at:
                    attempt.completed_at = now
                    attempt.save()
                return redirect('review_answers', exam_id=exam.id)
            # If no end time set, set to 0
            minutes = 0
            seconds = 0
        
        context = {
            "exam": exam,
            "question_list": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "page_number": int(page_number),
            "start_question_number": start_question_number,
            "secs": str(seconds).zfill(2),
            "mins": str(minutes),
            "student_started_at": attempt.started_at,
            "student_end_time": attempt.end_time,
            "answers": answers,
        }
        
        # Simple page load timing
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[PAGE LOAD] /exams/student/appear/{id}/ - {execution_time:.3f}s")
        print(f"[PAGE LOAD] Questions: {len(selected_questions)}, Page: {page_number}/{paginator.num_pages}")
        
        return render(request, 'exam/giveExam.html', context)
    
    if request.method == 'POST':
        paper = request.POST['paper']
        examMain = Exam_Model.objects.select_related('question_paper').get(name=paper)
        attempt_id = request.session.get(f'exam_{examMain.id}_attempt_id')
        attempt = StuExamAttempt.objects.select_related('exam', 'qpaper').prefetch_related('selected_questions').get(
            id=attempt_id, student=student, exam=examMain
        )
        
        # Get the questions selected for this attempt
        selected_questions = list(attempt.selected_questions.all().order_by('qno'))
        
        paginator = Paginator(selected_questions, 5)
        page_number = int(request.POST.get('page', 1))
        answers = request.session.get(f'exam_{examMain.id}_answers', {})
        
        # Collect answers from the current page
        for ques in paginator.get_page(page_number).object_list:
            ans = request.POST.get(str(ques.qno), None)
            if ans is not None:
                answers[str(ques.qno)] = ans
        request.session[f'exam_{examMain.id}_answers'] = answers

        # Navigation logic
        if 'prev_page' in request.POST:
            prev_page = max(1, page_number - 1)
            return redirect(f"{request.path}?page={prev_page}")

        if 'next_page' in request.POST:
            next_page = min(paginator.num_pages, page_number + 1)
            return redirect(f"{request.path}?page={next_page}")

        # Final submit
        if 'final_submit' in request.POST:
            attempt.questions.clear()
            student_questions = []
            # Collect short answer validation requests
            short_answer_requests = []
            short_answer_indices = []  # To map back to questions
            for idx, ques in enumerate(selected_questions):
                student_ans = answers.get(str(ques.qno), "")
                if ques.question_type == 'MCQ':
                    student_question = Stu_Question(
                        student=student,
                        question=ques.question,
                        optionA=ques.optionA or '',
                        optionB=ques.optionB or '',
                        optionC=ques.optionC or '',
                        optionD=ques.optionD or '',
                        answer=ques.mcq_answer or '',
                        choice=answers.get(str(ques.qno), "")
                    )
                elif ques.question_type == 'SHORT':
                    student_question = Stu_Question(
                        student=student,
                        question=ques.question,
                        optionA='',
                        optionB='',
                        optionC='',
                        optionD='',
                        answer=ques.short_answer or '',
                        choice=answers.get(str(ques.qno), ""),
                        # Will update marks_awarded and llm_explanation after LLM call
                    )
                    short_answer_requests.append(
                        ShortAnswerValidationRequest(
                            question=ques.question,
                            correct_answer=ques.short_answer or '',
                            student_answer=student_ans or '',
                            max_marks=ques.max_marks
                        )
                    )
                    short_answer_indices.append(idx)
                student_questions.append(student_question)
            created_questions = Stu_Question.objects.bulk_create(student_questions)
            attempt.questions.add(*created_questions)
            attempt.completed_at = timezone.now()
            examScore = 0
            # Collect short answer validation requests
            short_answer_requests = []
            short_answer_indices = []  # To map back to questions
            for idx, ques in enumerate(selected_questions):
                student_ans = answers.get(str(ques.qno), "")
                if ques.question_type == 'MCQ':
                    if student_ans.upper() == (ques.mcq_answer or '').upper():
                        examScore += ques.max_marks
                elif ques.question_type == 'SHORT':
                    short_answer_requests.append(
                        ShortAnswerValidationRequest(
                            question=ques.question,
                            correct_answer=ques.short_answer or '',
                            student_answer=student_ans or '',
                            max_marks=ques.max_marks
                        )
                    )
                    short_answer_indices.append(idx)
            # Batch validate short answers with LLM
            if short_answer_requests:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                results = validate_short_answers_with_llm(short_answer_requests, client=client)
                # Update created Stu_Question objects with LLM feedback
                for i, result in enumerate(results):
                    idx = short_answer_indices[i]
                    # Find the corresponding Stu_Question (SHORT) object
                    for q in created_questions:
                        if q.question == selected_questions[idx].question and q.answer == (selected_questions[idx].short_answer or ''):
                            q.marks_awarded = result.marks_awarded
                            q.llm_explanation = result.explanation
                            q.save()
                            break
                    examScore += result.marks_awarded
            attempt.score = examScore
            attempt.save()
            if f'exam_{examMain.id}_answers' in request.session:
                del request.session[f'exam_{examMain.id}_answers']
            if f'exam_{examMain.id}_attempt_id' in request.session:
                del request.session[f'exam_{examMain.id}_attempt_id']
            return redirect('review_answers', exam_id=examMain.id)

        # If none matched, reload current page
        return redirect(f"{request.path}?page={page_number}")

@login_required(login_url='login')
def view_exam_attempts(request, exam_id):
    """View all attempts for a specific exam"""
    student = request.user
    exam = Exam_Model.objects.get(pk=exam_id)
    attempts = StuExamAttempt.objects.filter(student=student, exam=exam).order_by('-started_at')
    
    attempts_data = []
    for attempt in attempts:
        attempts_data.append({
            'attempt': attempt,
            'score': attempt.score,
            'started_at': attempt.started_at,
            'completed_at': attempt.completed_at,
            'duration': attempt.completed_at - attempt.started_at if attempt.completed_at else None,
            'question_count': attempt.selected_questions.count()
        })
    
    return render(request, 'exam/exam_attempts.html', {
        'exam': exam,
        'attempts': attempts_data
    })

@login_required(login_url='login')
def review_answers(request, exam_id):
    student = request.user
    exam = Exam_Model.objects.get(pk=exam_id)
    attempt_id = request.GET.get('attempt_id')
    from student.models import StuExamAttempt
    
    # Optimize query with prefetch_related
    if attempt_id:
        attempt = StuExamAttempt.objects.prefetch_related('questions', 'selected_questions').filter(student=student, exam=exam, id=attempt_id).first()
    else:
        attempt = StuExamAttempt.objects.prefetch_related('questions', 'selected_questions').filter(student=student, exam=exam).order_by('-started_at').first()
    
    if not attempt:
        return render(request, 'exam/review_answers.html', {'exam': exam, 'review_data': [], 'summary': {}})
    
    # Get the questions from the question bank that were selected for this attempt
    questions_from_bank = list(attempt.get_selected_questions())
    
    # Get the student's submitted answers and map them by question text for easy lookup
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
        marks_awarded = 0
        llm_explanation = ""
        
        if ques_db.question_type == 'MCQ':
            is_correct = (student_ans.upper() == (ques_db.mcq_answer or '').upper())
            if student_question:
                marks_awarded = ques_db.max_marks if is_correct else 0
        elif ques_db.question_type == 'SHORT':
            if student_question:
                marks_awarded = student_question.marks_awarded
                llm_explanation = student_question.llm_explanation
                is_correct = marks_awarded == ques_db.max_marks

        review_data.append({
            'question_type': ques_db.question_type,
            'question': ques_db.question,
            'optionA': getattr(ques_db, 'optionA', ''),
            'optionB': getattr(ques_db, 'optionB', ''),
            'optionC': getattr(ques_db, 'optionC', ''),
            'optionD': getattr(ques_db, 'optionD', ''),
            'mcq_answer': getattr(ques_db, 'mcq_answer', ''),
            'short_answer': ques_db.short_answer,
            'student_answer': student_ans,
            'is_correct': is_correct,
            'solution': getattr(ques_db, 'solution', ''),
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
    
    return render(request, 'exam/review_answers.html', {
        'exam': exam,
        'review_data': review_data,
        'summary': summary
    })

def upload_questions_excel(request):
    from django.utils.safestring import mark_safe
    preview_data = None
    error_rows = []
    error_columns = set()
    columns = []
    file_b64 = None
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            # Step 1: File upload and validation
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file)
                required_columns = ['question', 'optionA', 'optionB', 'optionC', 'optionD', 'answer', 'max_marks']
                optional_columns = ['solution']
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    messages.error(request, f'Excel file is missing required columns: {", ".join(missing_cols)}.')
                    return render(request, 'exam/upload_questions_excel.html')
                # Validate each row
                for idx, row in df.iterrows():
                    row_errors = []
                    for col in required_columns:
                        value = row[col]
                        if pd.isna(value):
                            row_errors.append(col)
                            error_columns.add(col)
                        elif col == 'max_marks':
                            try:
                                int(value)
                            except Exception:
                                row_errors.append(col)
                                error_columns.add(col)
                    if row_errors:
                        error_rows.append({'row': idx+2, 'columns': row_errors})  # +2 for Excel row number (header + 1-based)
                preview_data = df.fillna('').to_dict(orient='records')
                columns = df.columns.tolist()
                # Store the file in base64 in a hidden field for the next step
                memfile = io.BytesIO()
                df.to_csv(memfile, index=False)
                memfile.seek(0)
                file_b64 = base64.b64encode(memfile.read()).decode('utf-8')
                return render(request, 'exam/upload_questions_excel.html', {
                    'preview_data': preview_data,
                    'columns': columns,
                    'error_rows': error_rows,
                    'error_columns': list(error_columns),
                    'file_b64': file_b64,
                })
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
        elif 'file_b64' in request.POST:
            # Step 2: Confirm and upload selected rows
            file_b64 = request.POST['file_b64']
            selected_rows = request.POST.getlist('selected_rows')
            try:
                csv_bytes = base64.b64decode(file_b64)
                df = pd.read_csv(io.BytesIO(csv_bytes))
                required_columns = ['question', 'optionA', 'optionB', 'optionC', 'optionD', 'answer', 'max_marks']
                # Save only selected rows
                count = 0
                for idx, row in df.iterrows():
                    if str(idx) in selected_rows:
                        # Validate again before saving
                        row_valid = True
                        for col in required_columns:
                            value = row[col]
                            if pd.isna(value):
                                row_valid = False
                            elif col == 'max_marks':
                                try:
                                    int(value)
                                except Exception:
                                    row_valid = False
                        if not row_valid:
                            continue
                        Question_DB.objects.create(
                            question=row['question'],
                            optionA=row['optionA'],
                            optionB=row['optionB'],
                            optionC=row['optionC'],
                            optionD=row['optionD'],
                            answer=row['answer'],
                            max_marks=int(row['max_marks']),
                            solution=row.get('solution', ''),  # Optional field
                            professor=request.user
                        )
                        count += 1
                if count:
                    messages.success(request, f'{count} questions uploaded successfully!')
                else:
                    messages.warning(request, 'No valid rows were selected for upload.')
                return render(request, 'exam/upload_questions_excel.html')
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
    return render(request, 'exam/upload_questions_excel.html')
