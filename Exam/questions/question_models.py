from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from course.models import Topic

class Question_DB(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('SHORT', 'Short Answer'),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='MCQ',
        help_text="Type of question: MCQ or Short Answer"
    )
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)
    question = models.TextField(help_text="Question text (supports HTML/markdown formatting)")
    # MCQ fields
    optionA = models.TextField(blank=True, null=True, help_text="Option A (supports HTML/markdown formatting)")
    optionB = models.TextField(blank=True, null=True, help_text="Option B (supports HTML/markdown formatting)")
    optionC = models.TextField(blank=True, null=True, help_text="Option C (supports HTML/markdown formatting)")
    optionD = models.TextField(blank=True, null=True, help_text="Option D (supports HTML/markdown formatting)")
    mcq_answer = models.CharField(max_length=1, blank=True, null=True, help_text="Correct option for MCQ (A/B/C/D)")
    short_answer = models.TextField(blank=True, null=True, help_text="Expected/model answer for short answer questions")
    max_marks = models.IntegerField(default=0)
    solution = models.TextField(blank=True, null=True, help_text="Detailed explanation of the correct answer (supports HTML/markdown formatting)")

    class Meta:
        indexes = [
            models.Index(fields=['professor']),
            models.Index(fields=['qno']),
        ]

    def __str__(self):
        return f'Question No.{self.qno}: {self.question[:50]}...'

    def get_question_display(self):
        """Return question with HTML formatting"""
        from django.utils.safestring import mark_safe
        return mark_safe(self.question)

    def get_option_display(self, option):
        """Return option with HTML formatting"""
        from django.utils.safestring import mark_safe
        option_text = getattr(self, f'option{option}', '')
        return mark_safe(option_text)

    def get_solution_display(self):
        """Return solution with HTML formatting"""
        from django.utils.safestring import mark_safe
        return mark_safe(self.solution) if self.solution else ''


class QForm(ModelForm):
    class Meta:
        model = Question_DB
        fields = '__all__'
        exclude = ['qno']
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'question': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your question here. You can use HTML tags like <b>bold</b>, <i>italic</i>, <ul><li>lists</li></ul>, or <img src="url"> for images.'
            }),
            'optionA': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option A (MCQ only)'
            }),
            'optionB': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option B (MCQ only)'
            }),
            'optionC': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option C (MCQ only)'
            }),
            'optionD': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option D (MCQ only)'
            }),
            'mcq_answer': forms.TextInput(attrs = {'class': 'form-control', 'placeholder': 'Correct option (A/B/C/D) for MCQ only'}),
            'short_answer': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Expected/model answer for short answer (mandatory)'
            }),
            'max_marks': forms.NumberInput(attrs = {'class': 'form-control'}),
            'solution': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter detailed explanation. You can use HTML tags for formatting like <b>bold</b>, <i>italic</i>, <ul><li>bullet points</li></ul>, or <code>code blocks</code>.'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        qtype = cleaned_data.get('question_type')
        if qtype == 'MCQ':
            for opt in ['optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer']:
                if not cleaned_data.get(opt):
                    self.add_error(opt, 'This field is required for MCQ.')
            # Clear short_answer for MCQ
            cleaned_data['short_answer'] = ''
        elif qtype == 'SHORT':
            if not cleaned_data.get('short_answer'):
                self.add_error('short_answer', 'This field is required for short answer questions.')
            # Clear mcq_answer for short answer
            cleaned_data['mcq_answer'] = ''
        return cleaned_data