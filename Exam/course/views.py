from django.shortcuts import render, redirect
from django.views.generic import ListView
from .models import Course, CourseRegistration, StudentAcceptance, Grade

# List all courses
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'faculty/manage_courses.html', {'courses': courses})

# List all course registrations (example implementation)
class CourseRegistrationListView(ListView):
    model = CourseRegistration
    template_name = 'faculty/course_registration_list.html'
    context_object_name = 'registrations'

def course_registration(request):
    if request.method == 'POST':
        return _extracted_from_course_registration_(request)
    courses = Course.objects.all()
    students = StudentAcceptance.objects.filter(has_paid_acceptance_fee=True, has_paid_school_fees=True)
    sessions = Session.objects.all()
    return render(request, 'course_registration.html', {'courses': courses, 'students': students, 'sessions': sessions})


# TODO Rename this here and in `course_registration`
def _extracted_from_course_registration_(request):
    student_id = request.POST.get('student_id')
    course_id = request.POST.get('course_id')
    session_id = request.POST.get('session_id')
    student = StudentAcceptance.objects.get(id=student_id)
    course = Course.objects.get(id=course_id)
    session = Session.objects.get(id=session_id)

    if not student.has_paid_acceptance_fee or not student.has_paid_school_fees:
        return render(request, 'error.html', {'message': 'Student not eligible for course registration.'})
    if student.credit_units_limit < course.credit_units:
        return render(request, 'error.html', {'message': 'Credit units limit exceeded.'})
    CourseRegistration.objects.create(student=student, course=course, session=session)
    return redirect('course_list')

