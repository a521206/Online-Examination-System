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
    marks_awarded = models.FloatField(default=0)
    llm_explanation = models.TextField(blank=True, default='')

class StuExamAttempt(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam_Model, on_delete=models.CASCADE)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Stu_Question)
    selected_questions = models.ManyToManyField(Question_DB, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    random_qids = models.CharField(max_length=500, blank=True, null=True)  # Keep for backward compatibility

    class Meta:
        indexes = [
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['started_at']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['student', 'exam', 'started_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.exam.name} - {self.started_at}"
    
    def save(self, *args, **kwargs):
        # Set started_at if not already set
        if not self.started_at:
            from django.utils import timezone
            self.started_at = timezone.now()
        
        # Set end_time to 1 hour after started_at if not already set
        if not self.end_time and self.started_at:
            from datetime import timedelta
            self.end_time = self.started_at + timedelta(hours=1)
        
        super().save(*args, **kwargs)
    
    def get_selected_questions(self):
        """Get the questions selected for this attempt - optimized version"""
        if self.selected_questions.exists():
            # Use prefetch_related if not already done
            return self.selected_questions.all().order_by('qno')
        elif self.random_qids:
            # Fallback to old method for backward compatibility
            qids = [int(qid) for qid in self.random_qids.split(',')]
            return Question_DB.objects.filter(qno__in=qids).order_by('qno')
        else:
            # If no questions selected, return first 10 from question paper
            return self.qpaper.questions.all()[:10]


class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    attempts = models.ManyToManyField(StuExamAttempt)

    def __str__(self):
        return str(self.student.username) +" -StuResults_DB"