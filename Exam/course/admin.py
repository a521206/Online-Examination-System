from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points')
    search_fields = ('name',)
    ordering = ('points',)

@admin.register(StudentAcceptance)
class StudentAcceptanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'matrix_No', 'has_paid_acceptance_fee', 'has_paid_school_fees', 'credit_units_limit')
    list_filter = ('has_paid_acceptance_fee', 'has_paid_school_fees')
    search_fields = ('name', 'matrix_No__reg_No', 'matrix_No__first_Name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_Code', 'credit_units')
    search_fields = ('name', 'course_Code', 'description')
    list_filter = ('credit_units',)

@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'session', 'grade')
    list_filter = ('session', 'grade', 'course')
    search_fields = ('student__name', 'course__name', 'course__course_Code')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')
    list_filter = ('course',)
    search_fields = ('name', 'course__name')
