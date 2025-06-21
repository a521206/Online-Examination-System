from django.contrib import admin
from tuition.models import *
# Register your models here.

@admin.register(StudentWallet)
class StudentWalletAdmin(admin.ModelAdmin):
    list_display = ('student', 'balance')
    list_filter = ('balance',)
    search_fields = ('student__first_name', 'student__last_name', 'student__username')

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('wallet__student__first_name', 'wallet__student__last_name')
    readonly_fields = ('timestamp',)

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_borrowed')
    list_filter = ('is_borrowed',)
    search_fields = ('title', 'author')

@admin.register(StudentInvolvement)
class StudentInvolvementAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'is_cleared')
    list_filter = ('is_cleared',)
    search_fields = ('student__first_name', 'student__last_name', 'activity')

@admin.register(ResultApproval)
class ResultApprovalAdmin(admin.ModelAdmin):
    list_display = ('student', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('student__first_name', 'student__last_name')