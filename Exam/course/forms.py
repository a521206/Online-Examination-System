from django import forms
from .models import Course, Topic

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'course_Code', 'credit_units']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'course_Code': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_units': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        } 