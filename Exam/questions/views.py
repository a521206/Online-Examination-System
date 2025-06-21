from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.models import Group
from student.models import *
from django.utils import timezone
from student.models import StuExam_DB,StuResults_DB
from questions.questionpaper_models import QPForm
from questions.question_models import QForm, Question_DB
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
    return render(request,'exam/previousstudent.html',{
        'exams':list_un,
        'completed':list_of_completed
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
            if StuExam_DB.objects.filter(student=student,examname=exam.name,completed=1).exists():
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
        if StuExam_DB.objects.filter(examname=exam.name,completed=1).exists():
            students_filter = StuExam_DB.objects.filter(examname=exam.name,completed=1)
            for student in students_filter:
                key = str(student.student) + " " + str(student.examname) + " " + str(student.qpaper.qPaperTitle)
                dicts[key] = student.score
    return render(request, 'exam/resultsstudent.html', {
        'students':dicts
    })

@login_required(login_url='login')
def view_exams_student(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    list_un = []
    for exam in exams:
        if StuExam_DB.objects.filter(examname=exam.name ,student=request.user).exists():
            if StuExam_DB.objects.get(examname=exam.name,student=request.user).completed == 1:
                list_of_completed.append(exam)
        else:
            list_un.append(exam)

    return render(request,'exam/mainexamstudent.html',{
        'exams':list_un,
        'completed':list_of_completed
    })

@login_required(login_url='login')
def view_students_attendance(request):
    exams = Exam_Model.objects.all()
    list_of_completed = []
    list_un = []
    for exam in exams:
        if StuExam_DB.objects.filter(examname=exam.name ,student=request.user).exists():
            if StuExam_DB.objects.get(examname=exam.name,student=request.user).completed == 1:
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

@login_required(login_url='login')
def appear_exam(request, id):
    student = request.user
    from .question_models import Question_DB
    QUESTIONS_PER_PAGE = 5
    if request.method == 'GET':
        exam = Exam_Model.objects.get(pk=id)
        # Create a new attempt for each exam start
        attempt_id = request.session.get(f'exam_{exam.id}_attempt_id')
        if attempt_id:
            try:
                attempt = StuExamAttempt.objects.get(id=attempt_id, student=student, exam=exam)
            except StuExamAttempt.DoesNotExist:
                attempt = None
        else:
            attempt = None
        if not attempt:
            attempt = StuExamAttempt.objects.create(student=student, exam=exam, qpaper=exam.question_paper)
            request.session[f'exam_{exam.id}_attempt_id'] = attempt.id
        # Randomize questions for this attempt
        all_questions = list(exam.question_paper.questions.all())
        if len(all_questions) > 10:
            if not attempt.random_qids:
                random_qs = random.sample(all_questions, 10)
                attempt.random_qids = ','.join(str(q.qno) for q in random_qs)
                attempt.save()
            else:
                random_qs = [q for q in all_questions if str(q.qno) in attempt.random_qids.split(',')]
        else:
            random_qs = all_questions
        paginator = Paginator(random_qs, QUESTIONS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        answers = request.session.get(f'exam_{exam.id}_answers', {})
        context = {
            "exam": exam,
            "question_list": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "page_number": int(page_number),
            "secs": "00",  # Timer logic can be added if needed
            "mins": "00",
            "student_started_at": attempt.started_at,
            "student_end_time": None,
            "answers": answers,
        }
        return render(request, 'exam/giveExam.html', context)
    if request.method == 'POST':
        paper = request.POST['paper']
        examMain = Exam_Model.objects.get(name=paper)
        attempt_id = request.session.get(f'exam_{examMain.id}_attempt_id')
        attempt = StuExamAttempt.objects.get(id=attempt_id, student=student, exam=examMain)
        all_questions = list(examMain.question_paper.questions.all())
        if attempt.random_qids:
            qids = [int(qid) for qid in attempt.random_qids.split(',')]
            qPaperQuestionsList = [q for q in all_questions if q.qno in qids]
        else:
            qPaperQuestionsList = all_questions[:10]
        paginator = Paginator(qPaperQuestionsList, 5)
        page_number = int(request.POST.get('page', 1))
        answers = request.session.get(f'exam_{examMain.id}_answers', {})
        for ques in paginator.get_page(page_number).object_list:
            ans = request.POST.get(ques.question, None)
            if ans is not None:
                answers[str(ques.qno)] = ans
        request.session[f'exam_{examMain.id}_answers'] = answers
        if page_number < paginator.num_pages and 'final_submit' not in request.POST:
            next_page = page_number + 1
            return redirect(f"{request.path}?page={next_page}")
        attempt.questions.clear()
        for ques in qPaperQuestionsList:
            student_question = Stu_Question.objects.create(
                student=student,
                question=ques.question,
                optionA=ques.optionA,
                optionB=ques.optionB,
                optionC=ques.optionC,
                optionD=ques.optionD,
                answer=ques.answer,
                choice=answers.get(str(ques.qno), "")
            )
            attempt.questions.add(student_question)
        attempt.completed_at = timezone.now()
        # Calculate score
        examScore = 0
        for ques in qPaperQuestionsList:
            student_ans = answers.get(str(ques.qno), "")
            if student_ans.lower() == ques.answer.lower() or student_ans == ques.answer:
                examScore += ques.max_marks
        attempt.score = examScore
        attempt.save()
        if f'exam_{examMain.id}_answers' in request.session:
            del request.session[f'exam_{examMain.id}_answers']
        if f'exam_{examMain.id}_attempt_id' in request.session:
            del request.session[f'exam_{examMain.id}_attempt_id']
        return redirect('review_answers', exam_id=examMain.id)

@login_required(login_url='login')
def review_answers(request, exam_id):
    student = request.user
    exam = Exam_Model.objects.get(pk=exam_id)
    attempt_id = request.GET.get('attempt_id')
    from student.models import StuExamAttempt
    if attempt_id:
        attempt = StuExamAttempt.objects.filter(student=student, exam=exam, id=attempt_id).first()
    else:
        attempt = StuExamAttempt.objects.filter(student=student, exam=exam).order_by('-started_at').first()
    if not attempt:
        return render(request, 'exam/review_answers.html', {'exam': exam, 'review_data': [], 'summary': {}})
    questions = exam.question_paper.questions.all()
    student_questions = attempt.questions.all()
    answer_map = {q.question: q.choice for q in student_questions}
    review_data = []
    total_marks = 0
    correct = 0
    wrong = 0
    not_attempted = 0
    total_possible_marks = 0
    for ques in questions:
        student_ans = answer_map.get(ques.question, "")
        is_correct = (student_ans.lower() == ques.answer.lower() or student_ans == ques.answer)
        review_data.append({
            'question': ques.question,
            'optionA': ques.optionA,
            'optionB': ques.optionB,
            'optionC': ques.optionC,
            'optionD': ques.optionD,
            'correct_answer': ques.answer,
            'student_answer': student_ans,
            'is_correct': is_correct
        })
        total_possible_marks += ques.max_marks
        if student_ans == "" or student_ans is None:
            not_attempted += 1
        elif is_correct:
            correct += 1
            total_marks += ques.max_marks
        else:
            wrong += 1
    return render(request, 'exam/review_answers.html', {
        'exam': exam,
        'review_data': review_data,
        'summary': {
            'total_marks': total_marks,
            'correct': correct,
            'wrong': wrong,
            'not_attempted': not_attempted,
            'total_possible_marks': total_possible_marks
        }
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
