from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from datetime import datetime
from .questionpaper_models import Question_Paper
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class Exam_Model(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    total_marks = models.IntegerField()
    question_paper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, related_name='exams')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    num_questions = models.PositiveIntegerField(
        default=10,
        help_text="Number of random questions to select for this exam. Must be less than or equal to the number of questions in the question paper."
    )

    def clean(self):
        super().clean()
        if self.question_paper and self.num_questions > self.question_paper.questions.count():
            raise ValidationError({'num_questions': f"Cannot select more than {self.question_paper.questions.count()} questions for this exam."})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timedelta(minutes=60)
        super().save(*args, **kwargs)


class ExamForm(ModelForm):
    def __init__(self,professor,*args,**kwargs):
        super (ExamForm,self ).__init__(*args,**kwargs) 
        self.fields['question_paper'].queryset = Question_Paper.objects.filter(professor=professor)

    class Meta:
        model = Exam_Model
        fields = '__all__'
        exclude = ['professor']
        widgets = {
            'name': forms.TextInput(attrs = {'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs = {'class':'form-control'}),
            'start_time': forms.DateTimeInput(attrs = {'class':'form-control'}),
            'end_time': forms.DateTimeInput(attrs = {'class':'form-control'}),
            'num_questions': forms.NumberInput(attrs = {'class':'form-control'}),
        }