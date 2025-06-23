from django.urls import path
from . import views
urlpatterns = [
    path('prof/viewexams/',views.view_exams_prof,name="view_exams"),
    path('prof/viewpreviousexams/',views.view_previousexams_prof,name="faculty-previous"),
    path('prof/viewresults/',views.view_results_prof,name="faculty-result"),
    path('prof/addquestions/',views.add_questions,name="faculty-addquestions"),
    path('prof/addnewquestionpaper/',views.add_question_paper,name="faculty-add_question_paper"),
    path('prof/viewstudents/',views.view_students_prof,name="faculty-student"),
    path('prof/upload-questions-excel/',views.upload_questions_excel,name="upload_questions_excel"),
]