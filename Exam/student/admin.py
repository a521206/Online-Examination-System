from django.contrib import admin
from .models import *

@admin.action(description='Mark selected as Completed')
def mark_completed(modeladmin, request, queryset):
    queryset.update(completed=1)

@admin.action(description='Reset selected Exams')
def reset_exam(modeladmin, request, queryset):
    queryset.update(completed=0, score=0)

class StuExamDBAdmin(admin.ModelAdmin):
    list_display = ('student', 'examname', 'qpaper', 'completed', 'score')
    actions = [mark_completed, reset_exam]
    change_list_template = "admin/student/stuexam_db_changelist.html"

admin.site.register(StudentInfo)
admin.site.register(Stu_Question)
admin.site.register(StuExam_DB, StuExamDBAdmin)
admin.site.register(StuResults_DB)