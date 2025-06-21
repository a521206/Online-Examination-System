from django.contrib import admin
from .models import StudentPreferenceModel
# Register your models here.

@admin.register(StudentPreferenceModel)
class StudentPreferenceModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'sendEmailOnLogin')
    list_filter = ('sendEmailOnLogin',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')