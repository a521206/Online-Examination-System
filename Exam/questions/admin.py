from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from .models import Exam_Model
from .question_models import Question_DB
from .questionpaper_models import Question_Paper
from django.urls import reverse

class QuestionDBAdmin(admin.ModelAdmin):
    change_list_template = "admin/questions/question_db_changelist.html"
    list_display = ['qno', 'question', 'answer', 'max_marks', 'professor']
    list_filter = ['professor', 'max_marks']
    search_fields = ['question', 'answer']
    fieldsets = (
        ('Question Details', {
            'fields': ('professor', 'question', 'max_marks')
        }),
        ('Options', {
            'fields': ('optionA', 'optionB', 'optionC', 'optionD')
        }),
        ('Answer & Solution', {
            'fields': ('answer', 'solution'),
            'description': 'Provide the correct answer and detailed explanation'
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-questions-excel/', self.admin_site.admin_view(self.upload_excel_redirect), name='upload_questions_excel_admin'),
        ]
        return custom_urls + urls

    def upload_excel_redirect(self, request):
        from django.shortcuts import redirect
        return redirect(reverse('upload_questions_excel'))

admin.site.register(Question_DB, QuestionDBAdmin)
admin.site.register(Question_Paper)
#admin.site.register(Special_Students)
admin.site.register(Exam_Model)