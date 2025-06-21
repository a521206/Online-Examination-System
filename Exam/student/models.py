from django.db import models
from django.contrib.auth.models import User
from questions.question_models import Question_DB
from questions.questionpaper_models import Question_Paper
from questions.models import Exam_Model

class StudentInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    stream = models.CharField(max_length=50, blank=True)
    picture = models.ImageField(upload_to = 'student_profile_pics', blank=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Student Info'

class Stu_Question(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=100)
    optionA = models.CharField(max_length=100, blank=True, default='')
    optionB = models.CharField(max_length=100, blank=True, default='')
    optionC = models.CharField(max_length=100, blank=True, default='')
    optionD = models.CharField(max_length=100, blank=True, default='')
    answer = models.CharField(max_length=200, blank=True, default='')
    choice = models.CharField(max_length=10, blank=True, default='')

class StuExamAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam_Model, on_delete=models.CASCADE)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Stu_Question)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    random_qids = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.name} - {self.started_at}"

class StuExam_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    examname = models.CharField(max_length=100)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True)
    questions = models.ManyToManyField(Stu_Question)
    score = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.student.username) +" " + str(self.examname) + " " + str(self.qpaper.qPaperTitle) + "-StuExam_DB"


class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    exams = models.ManyToManyField(StuExam_DB)

    def __str__(self):
        return str(self.student.username) +" -StuResults_DB"