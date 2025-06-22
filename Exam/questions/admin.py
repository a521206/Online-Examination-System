from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from .models import Exam_Model
from .question_models import Question_DB, QForm
from .questionpaper_models import Question_Paper
from django.urls import reverse

class QuestionDBAdmin(admin.ModelAdmin):
    change_list_template = "admin/questions/question_db_changelist.html"
    list_display = ['qno', 'question', 'question_type', 'mcq_answer', 'short_answer', 'max_marks', 'professor']
    list_filter = ['professor', 'max_marks', 'question_type']
    search_fields = ['question', 'mcq_answer', 'short_answer']
    fieldsets = (
        ('Question Details', {
            'fields': ('professor', 'question_type', 'question', 'max_marks')
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

admin.site.register(Question_DB, QuestionDBAdmin)
admin.site.register(Question_Paper)
#admin.site.register(Special_Students)
admin.site.register(Exam_Model)