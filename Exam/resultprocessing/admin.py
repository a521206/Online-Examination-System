from django.contrib import admin
from resultprocessing.models import ResultStudent, ResultCourse, Score, ConfigMarks
# Register your models here.

@admin.register(ResultStudent)
class ResultStudentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ResultCourse)
class ResultCourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'credit_units')
    search_fields = ('name',)
    list_filter = ('credit_units',)

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'assignment_score', 'test_score', 'exam_score', 'total_score', 'is_carry_over')
    list_filter = ('is_carry_over', 'course')
    search_fields = ('student__name', 'course__name')
    readonly_fields = ('total_score',)

@admin.register(ConfigMarks)
class ConfigMarksAdmin(admin.ModelAdmin):
    list_display = ('mark_score', 'grade_letter', 'gp')
    search_fields = ('grade_letter',)
    ordering = ('mark_score',)

