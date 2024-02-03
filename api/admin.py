from django.contrib import admin
from .models import User, Transaction, EmailVerificationToken, Expense, Income
# Register your models here.

admin.site.register(EmailVerificationToken)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'user', 'amount', 'description']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'user', 'amount', 'description']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'added_by', 'liney', 'diney',
                    'amount', 'is_verified', 'to_be_verified_by', ]
    readonly_fields = ['transaction_type', 'added_by', 'liney', 'diney', 'transaction_detail',
                       'amount', 'is_verified', 'to_be_verified_by', ]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_email_verified',  'date_joined']
    list_filter = ('is_admin', 'is_email_verified')
    search_fields = ['username', 'email']
