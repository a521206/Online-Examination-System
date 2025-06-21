from django.contrib import admin
from .models import *

@admin.action(description='Reset selected Exam Attempts')
def reset_exam_attempts(modeladmin, request, queryset):
    queryset.update(score=0, completed_at=None)

class StuExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'qpaper', 'started_at', 'completed_at', 'score', 'get_question_count')
    list_filter = ('exam', 'student', 'started_at', 'completed_at')
    search_fields = ('student__username', 'exam__name', 'qpaper__qPaperTitle')
    readonly_fields = ('started_at', 'random_qids', 'get_question_count')
    actions = [reset_exam_attempts]
    ordering = ('-started_at',)
    
    def get_question_count(self, obj):
        return obj.selected_questions.count()
    get_question_count.short_description = 'Questions Selected'

class StuResultsDBAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_attempt_count', 'get_total_score')
    list_filter = ('student',)
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('get_attempt_count', 'get_total_score')
    
    def get_attempt_count(self, obj):
        return obj.attempts.count()
    get_attempt_count.short_description = 'Number of Attempts'
    
    def get_total_score(self, obj):
        total = sum(attempt.score for attempt in obj.attempts.all())
        return total
    get_total_score.short_description = 'Total Score'

admin.site.register(StudentInfo)
admin.site.register(Stu_Question)
admin.site.register(StuExamAttempt, StuExamAttemptAdmin)
admin.site.register(StuResults_DB, StuResultsDBAdmin)