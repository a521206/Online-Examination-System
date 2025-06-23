from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from .question_models import Question_DB
from course.models import Topic, Course
from django import forms

class Question_Paper(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='question_papers', null=True, blank=True)
    qPaperTitle = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question_DB)

    def __str__(self):
        return f' Question Paper Title :- {self.qPaperTitle}\n'


class QPForm(ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, label="Subject")
    
    def __init__(self,professor,*args,**kwargs):
        super (QPForm,self ).__init__(*args,**kwargs) 
        self.fields['questions'].queryset = Question_DB.objects.filter(professor=professor)
        self.fields['topic'].queryset = Topic.objects.none()

        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['topic'].queryset = Topic.objects.filter(course_id=course_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Topic queryset
        elif self.instance.pk and self.instance.topic:
            self.fields['topic'].queryset = self.instance.topic.course.topics.order_by('name')

    class Meta:
        model = Question_Paper
        fields = ['course', 'topic', 'qPaperTitle', 'questions']
        exclude = ['professor']
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'qPaperTitle': forms.TextInput(attrs = {'class':'form-control'})
        }
