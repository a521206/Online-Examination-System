from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

class Question_DB(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)
    question = models.TextField(help_text="Question text (supports HTML/markdown formatting)")
    optionA = models.TextField(help_text="Option A (supports HTML/markdown formatting)")
    optionB = models.TextField(help_text="Option B (supports HTML/markdown formatting)")
    optionC = models.TextField(help_text="Option C (supports HTML/markdown formatting)")
    optionD = models.TextField(help_text="Option D (supports HTML/markdown formatting)")
    answer = models.CharField(max_length=200)
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
        exclude = ['qno', 'professor']
        widgets = {
            'question': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your question here. You can use HTML tags like <b>bold</b>, <i>italic</i>, <ul><li>lists</li></ul>, or <img src="url"> for images.'
            }),
            'optionA': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option A (supports HTML formatting)'
            }),
            'optionB': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option B (supports HTML formatting)'
            }),
            'optionC': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option C (supports HTML formatting)'
            }),
            'optionD': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Option D (supports HTML formatting)'
            }),
            'answer': forms.TextInput(attrs = {'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs = {'class': 'form-control'}),
            'solution': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter detailed explanation. You can use HTML tags for formatting like <b>bold</b>, <i>italic</i>, <ul><li>bullet points</li></ul>, or <code>code blocks</code>.'
            }),
        }