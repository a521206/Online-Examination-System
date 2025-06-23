from django.urls import path
from .views import course_list, CourseRegistrationListView, course_registration
from .professor_views import manage_courses, add_course, manage_topics, add_topic

urlpatterns = [
    # Student views
    path('courses/', course_list, name='course_list'),
    path('registrations/', CourseRegistrationListView.as_view(), name='registration_list'),
    path('register/', course_registration, name='course_registration'),

    # Professor views
    path('faculty/courses/', manage_courses, name='manage_courses'),
    path('faculty/courses/add/', add_course, name='add_course'),
    path('faculty/courses/<int:course_id>/topics/', manage_topics, name='manage_topics'),
    path('faculty/courses/<int:course_id>/topics/add/', add_topic, name='add_topic'),
]
