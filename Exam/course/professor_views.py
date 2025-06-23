from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Topic
from .forms import CourseForm, TopicForm

def is_professor(user):
    return user.groups.filter(name='Professor').exists()

@login_required
@user_passes_test(is_professor)
def manage_courses(request):
    courses = Course.objects.all()
    return render(request, 'faculty/manage_courses.html', {'courses': courses})

@login_required
@user_passes_test(is_professor)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_courses')
    else:
        form = CourseForm()
    return render(request, 'faculty/add_course.html', {'form': form})

@login_required
@user_passes_test(is_professor)
def manage_topics(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    topics = Topic.objects.filter(course=course)
    return render(request, 'faculty/manage_topics.html', {'topics': topics, 'course': course})

@login_required
@user_passes_test(is_professor)
def add_topic(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.course = course
            topic.save()
            return redirect('manage_topics', course_id=course.id)
    else:
        form = TopicForm()
    return render(request, 'faculty/add_topic.html', {'form': form, 'course': course}) 