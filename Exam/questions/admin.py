from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from .models import Exam_Model
from .question_models import Question_DB, QForm
from .questionpaper_models import Question_Paper
from django.urls import reverse
from django import forms

class QuestionDBAdmin(admin.ModelAdmin):
    change_list_template = "admin/questions/question_db_changelist.html"
    list_display = ['qno', 'question', 'question_type', 'mcq_answer', 'short_answer', 'max_marks', 'professor', 'question_image', 'solution_image']
    list_filter = ['professor', 'max_marks', 'question_type']
    search_fields = ['question', 'mcq_answer', 'short_answer']
    readonly_fields = ('question_image_preview', 'solution_image_preview',)
    fieldsets = (
        ('Question Details', {
            'fields': ('professor', 'question_type', 'question', 'max_marks')
        }),
        ('Images', {
            'fields': ('question_image', 'question_image_preview', 'solution_image', 'solution_image_preview')
        }),
        ('MCQ Options (for MCQ only)', {
            'fields': ('optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer')
        }),
        ('Short Answer (for Short Answer only)', {
            'fields': ('short_answer',)
        }),
        ('Solution', {
            'fields': ('solution',),
            'description': 'Provide a detailed explanation of the correct answer.'
        }),
    )
    form = QForm

    def question_image_preview(self, obj):
        if obj.question_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="150" height="150" /></a>', obj.question_image.url)
        return "(No Image)"
    question_image_preview.short_description = 'Question Image Preview'

    def solution_image_preview(self, obj):
        if obj.solution_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="150" height="150" /></a>', obj.solution_image.url)
        return "(No Image)"
    solution_image_preview.short_description = 'Solution Image Preview'

    class Media:
        js = ('js/question_type_toggle.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-questions-excel/', self.admin_site.admin_view(self.upload_excel_redirect), name='upload_questions_excel_admin'),
        ]
        return custom_urls + urls

    def upload_excel_redirect(self, request):
        from django.shortcuts import redirect
        return redirect(reverse('upload_questions_excel'))

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            qtype = obj.question_type
        else:
            qtype = request.GET.get('question_type', None)
        if qtype == 'MCQ':
            for f in ['optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer']:
                form.base_fields[f].required = True
            form.base_fields['short_answer'].required = False
        elif qtype == 'SHORT':
            for f in ['optionA', 'optionB', 'optionC', 'optionD', 'mcq_answer']:
                form.base_fields[f].required = False
            form.base_fields['short_answer'].required = True
        return form

class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('qPaperTitle', 'topic', 'get_course', 'professor')
    list_filter = ('topic', 'topic__course', 'professor')
    search_fields = ('qPaperTitle',)
    def get_course(self, obj):
        return obj.topic.course if obj.topic else None
    get_course.short_description = 'Course'

class ExamModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_paper', 'get_topic', 'get_course', 'professor', 'start_time', 'end_time')
    list_filter = ('question_paper__topic', 'question_paper__topic__course', 'professor')
    search_fields = ('name',)
    def get_topic(self, obj):
        return obj.question_paper.topic if obj.question_paper else None
    get_topic.short_description = 'Topic'
    def get_course(self, obj):
        return obj.question_paper.topic.course if obj.question_paper and obj.question_paper.topic else None
    get_course.short_description = 'Course'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        class CustomExamForm(form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                qp = self.initial.get('question_paper') or (obj.question_paper.pk if obj and obj.question_paper else None)
                if qp:
                    from .questionpaper_models import Question_Paper
                    try:
                        qpaper = Question_Paper.objects.get(pk=qp)
                        total_questions = qpaper.questions.count()
                        self.fields['num_questions'].help_text = f"Number of random questions to select for this exam. There are {total_questions} questions in the selected question paper. Must be less than or equal to this number."
                        self.fields['num_questions'].widget.attrs['max'] = total_questions
                        self.fields['num_questions'].widget.attrs['min'] = 1
                    except Exception:
                        pass
        return CustomExamForm

admin.site.register(Question_DB, QuestionDBAdmin)
admin.site.register(Question_Paper, QuestionPaperAdmin)
admin.site.register(Exam_Model, ExamModelAdmin)
#admin.site.register(Special_Students)