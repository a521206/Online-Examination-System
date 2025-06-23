from django.shortcuts import render,redirect
from django.views import View
from .forms import StudentForm, StudentInfoForm
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode 
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import account_activation_token
from django.core.mail import EmailMessage
import threading
from django.contrib.auth.models import User
from studentPreferences.models import StudentPreferenceModel
from django.contrib.auth.models import Group
from questions.models import Exam_Model
from questions.questionpaper_models import Question_Paper
from student.models import StuExamAttempt
from django.contrib.auth.forms import AuthenticationForm
from course.models import Course, Topic
from questions.services import process_exam_submission, prepare_review_data
from django.core.paginator import Paginator
import time
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from utils.performance_monitor import monitor_performance

@login_required(login_url='login')
def index(request):
    # Get statistics for the dashboard
    total_exams = Exam_Model.objects.count()
    completed_exams = StuExamAttempt.objects.filter(student=request.user).count()
    
    # Calculate average score
    attempts = StuExamAttempt.objects.filter(student=request.user)
    if attempts.exists():
        total_score = sum(attempt.score for attempt in attempts)
        average_score = (total_score / attempts.count()) if attempts.count() > 0 else 0
    else:
        average_score = 0
    
    context = {
        'total_exams': total_exams,
        'completed_exams': completed_exams,
        'average_score': average_score,
    }
    
    return render(request, 'student/index.html', context)

class Register(View):
    def get(self,request):
        student_form = StudentForm()
        student_info_form = StudentInfoForm()
        return render(request,'student/register.html',{'student_form':student_form,'student_info_form':student_info_form})
    
    def post(self,request):
        student_form = StudentForm(data=request.POST)
        student_info_form = StudentInfoForm(data=request.POST)
        email = request.POST['email']

        if student_form.is_valid() and student_info_form.is_valid():
            student = student_form.save(commit=False)
            student.first_name = student_form.cleaned_data.get('first_name', '')
            student.save()
            student.set_password(student.password)
            student.is_active = False
            my_group = Group.objects.get_or_create(name='Student')
            my_group[0].user_set.add(student)
            student.save()

            uidb64 = urlsafe_base64_encode(force_bytes(student.pk))
            domain = get_current_site(request).domain
            link = reverse('activate',kwargs={'uidb64':uidb64,'token':account_activation_token.make_token(student)})
            activate_url = 'http://' + domain +link
            email_subject = 'Activate your Exam Portal account'
            email_body = 'Hi.Please use this link to verify your account\n' + activate_url + ".\n\n You are receiving this message because you registered on " + domain +". If you didn't register please contact support team on " + domain 
            fromEmail = 'noreply@exam.com'
            email = EmailMessage(
				email_subject,
				email_body,
				fromEmail,
				[email],
            )
            student_info = student_info_form.save(commit=False)
            student_info.user = student
            if 'picture' in request.FILES:
                student_info.picture = request.FILES['picture']
            student_info.save()
            messages.success(request,"Registered Succesfully. Check Email for confirmation")
            EmailThread(email).start()
            return redirect('login')
        else:
            print(student_form.errors,student_info_form.errors)
            return render(request,'student/register.html',{'student_form':student_form,'student_info_form':student_info_form})
    
class LoginView(View):
    def get(self,request):
        form = AuthenticationForm()
        return render(request,'student/login.html', {'form': form})
    def post(self,request):
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                messages.error(request,"You are trying to login as student, but you have registered as faculty. We are redirecting you to faculty login. If you are having problem in logging in please reset password or contact admin")
                return redirect('faculty-login')
            if user.is_active:
                auth.login(request,user)
                student_pref = StudentPreferenceModel.objects.filter(user = request.user).exists()
                email = user.email
                email_subject = 'You Logged into your Portal account'
                email_body = "If you think someone else logged in. Please contact support or reset your password.\n\nYou are receving this message because you have enabled login email notifications in portal settings. If you don't want to recieve such emails in future please turn the login email notifications off in settings."
                fromEmail = 'noreply@exam.com'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    fromEmail,
                    [email],
                )
                if student_pref:
                    student = StudentPreferenceModel.objects.get(user=request.user)
                    sendEmail = student.sendEmailOnLogin 
                if not student_pref:
                    EmailThread(email).start()
                elif sendEmail:
                    EmailThread(email).start()
                messages.success(request,"Welcome, "+ user.username + ". You are now logged in.")
                return redirect('index')
        else:
            if username:
                user_qs = User.objects.filter(username=username)
                if user_qs.exists():
                    user = user_qs.first()
                    if not user.is_active:
                        messages.error(request,'Account not Activated')
                        return render(request,'student/login.html', {'form': form})
            messages.error(request,'Invalid credentials')
        return render(request,'student/login.html', {'form': form})

class LogoutView(View):
	def post(self,request):
		auth.logout(request)
		messages.success(request,'Logged Out')
		return redirect('login')

class EmailThread(threading.Thread):
	def __init__(self,email):
		self.email = email
		threading.Thread.__init__(self)

	
	def run(self):
		self.email.send(fail_silently = False)

class VerificationView(View):
	def get(self,request,uidb64,token):
		try:
			id = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=id)
			if not account_activation_token.check_token(user,token):
				messages.error(request,"User already Activated. Please Proceed With Login")
				return redirect("login")
			if user.is_active:
				return redirect('login')
			user.is_active = True
			user.save()
			messages.success(request,'Account activated Sucessfully')
			return redirect('login')
		except Exception as e:
			raise e
		return redirect('login')
	
@login_required(login_url='login')
def view_exams_student(request):
    stud = request.user
    permissions = has_group(stud, "Student")
    if not permissions:
        return redirect('index')

    course_id = request.GET.get('course_id')
    topic_id = request.GET.get('topic_id')

    # AJAX request for topics
    if course_id and not topic_id:
        topics = Topic.objects.filter(course_id=course_id).order_by('name')
        return render(request, 'partials/_topics_dropdown.html', {'topics': topics})

    # AJAX request for exams
    if topic_id:
        now = timezone.now()
        exams = Exam_Model.objects.filter(
            question_paper__topic_id=topic_id,
            start_time__lte=now,
            end_time__gte=now
        )
        return render(request, 'partials/_exam_list_student.html', {'exams': exams})

    # Initial view
    courses = Course.objects.all()
    return render(request, 'exam/mainexamstudent.html', {
        'courses': courses, 'student': stud,
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

@login_required(login_url='login')
def student_view_previous(request):
    stud = request.user
    permissions = has_group(stud, "Student")
    if not permissions:
        return redirect('index')
    attempts = StuExamAttempt.objects.filter(student=stud).order_by('-started_at')
    return render(request, 'exam/previousstudent.html', {'attempts': attempts})

@monitor_performance("appear_exam")
@login_required(login_url='login')
def appear_exam(request, id):
    start_time = time.time()
    student = request.user
    from questions.question_models import Question_DB
    QUESTIONS_PER_PAGE = 5
    if request.method == 'GET':
        exam = Exam_Model.objects.select_related('question_paper', 'professor').get(pk=id)
        attempt_id = request.session.get(f'exam_{exam.id}_attempt_id')
        attempt = None
        now = timezone.now()
        if attempt_id:
            try:
                attempt = StuExamAttempt.objects.select_related('exam', 'qpaper').prefetch_related('selected_questions').get(
                    id=attempt_id, student=student, exam=exam
                )
                if attempt.completed_at or (attempt.end_time and now >= attempt.end_time):
                    attempt = None
                    del request.session[f'exam_{exam.id}_attempt_id']
            except StuExamAttempt.DoesNotExist:
                attempt = None
        if not attempt:
            attempt = StuExamAttempt.objects.create(
                student=student, 
                exam=exam, 
                qpaper=exam.question_paper,
                started_at=timezone.now()
            )
            request.session[f'exam_{exam.id}_attempt_id'] = attempt.id
            all_questions = exam.question_paper.questions.all()
            question_count = all_questions.count()
            num_questions = getattr(exam, 'num_questions', 10)
            if question_count > num_questions:
                from django.db.models import Q
                import random
                all_qids = list(all_questions.values_list('qno', flat=True))
                if len(all_qids) > num_questions:
                    random_qids = random.sample(all_qids, num_questions)
                    random_qs = Question_DB.objects.filter(qno__in=random_qids)
                else:
                    random_qs = all_questions
                attempt.selected_questions.set(random_qs)
                attempt.random_qids = ','.join(str(q.qno) for q in random_qs)
            else:
                attempt.selected_questions.set(all_questions)
                attempt.random_qids = ','.join(str(q.qno) for q in all_questions)
            attempt.save()
        selected_questions = list(attempt.selected_questions.all().order_by('qno'))
        paginator = Paginator(selected_questions, QUESTIONS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        answers = request.session.get(f'exam_{exam.id}_answers', {})
        start_question_number = (page_obj.number - 1) * QUESTIONS_PER_PAGE + 1
        if attempt.end_time and now < attempt.end_time:
            time_remaining = attempt.end_time - now
            total_seconds = int(time_remaining.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
        else:
            if attempt.end_time and now >= attempt.end_time:
                if not attempt.completed_at:
                    attempt.completed_at = now
                    attempt.save()
                return redirect('review_answers', exam_id=exam.id)
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
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[PAGE LOAD] /student/appear/{id}/ - {execution_time:.3f}s")
        print(f"[PAGE LOAD] Questions: {len(selected_questions)}, Page: {page_number}/{paginator.num_pages}")
        return render(request, 'exam/giveExam.html', context)
    if request.method == 'POST':
        paper = request.POST['paper']
        examMain = Exam_Model.objects.select_related('question_paper').get(name=paper)
        attempt_id = request.session.get(f'exam_{examMain.id}_attempt_id')
        attempt = StuExamAttempt.objects.select_related('exam', 'qpaper').get(id=attempt_id, student=student, exam=examMain)
        paginator = Paginator(list(attempt.get_selected_questions()), 5)
        page_number = int(request.POST.get('page', 1))
        answers = request.session.get(f'exam_{examMain.id}_answers', {})
        for ques in paginator.get_page(page_number).object_list:
            ans = request.POST.get(str(ques.qno))
            if ans is not None:
                answers[str(ques.qno)] = ans
        request.session[f'exam_{examMain.id}_answers'] = answers
        if 'prev_page' in request.POST:
            prev_page = max(1, page_number - 1)
            return redirect(f"{request.path}?page={prev_page}")
        if 'next_page' in request.POST:
            next_page = min(paginator.num_pages, page_number + 1)
            return redirect(f"{request.path}?page={next_page}")
        if 'final_submit' in request.POST:
            process_exam_submission(attempt, answers)
            if f'exam_{examMain.id}_answers' in request.session:
                del request.session[f'exam_{examMain.id}_answers']
            if f'exam_{examMain.id}_attempt_id' in request.session:
                del request.session[f'exam_{examMain.id}_attempt_id']
            return redirect('review_answers', exam_id=examMain.id)
        return redirect(f"{request.path}?page={page_number}")

@login_required(login_url='login')
def view_exam_attempts(request, exam_id):
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
    if attempt_id:
        attempt = StuExamAttempt.objects.prefetch_related('questions', 'selected_questions').filter(student=student, exam=exam, id=attempt_id).first()
    else:
        attempt = StuExamAttempt.objects.prefetch_related('questions', 'selected_questions').filter(student=student, exam=exam).order_by('-started_at').first()
    if not attempt:
        return render(request, 'exam/review_answers.html', {'exam': exam, 'review_data': [], 'summary': {}})
    review_data, summary = prepare_review_data(attempt)
    return render(request, 'exam/review_answers.html', {
        'exam': exam,
        'review_data': review_data,
        'summary': summary,
    })

def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False
	
