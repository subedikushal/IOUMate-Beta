from __future__ import unicode_literals
from django.contrib.auth.hashers import make_password
import uuid
from django.utils import timezone
from django.core.validators import MinValueValidator
import datetime

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'), unique=True, primary_key=True)
    username = models.CharField(
        max_length=20, default='', unique=True, editable=False, db_index=True)
    first_name = models.CharField(
        max_length=20, blank=False, null=False)
    last_name = models.CharField(
        max_length=20, blank=False, null=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    friend_requests = ArrayField(models.CharField(
        max_length=20), default=list,    blank=True, null=True)
    friends = ArrayField(models.CharField(max_length=20), default=list,
                         blank=True, null=True)
    sent_friend_requests = ArrayField(
        models.CharField(max_length=20), default=list,  blank=True, null=True)

    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    # below two methods are required for making custom user model
    # For checking permissions. to keep it simple all admin have ALL permissons

    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


# an user can have many transaction but a transaction is associated with only two different users


class Transaction(models.Model):
    # lina pareny
    TRANSACTION_CHOICES = (
        ('C', 'Credit'),
        ('D', 'Debit')
    )
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_CHOICES)
    transaction_detail = models.CharField(
        max_length=120, blank=False, null=False)
    added_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="added_transactions", editable=False)
    liney = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='credit_transactions', editable=False)
    # dina parney
    diney = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='debit_transactions', editable=False)

    is_verified = models.BooleanField(default=False, editable=False)
    to_be_verified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions_to_be_verified')
    amount = models.DecimalField(
        max_digits=20, decimal_places=3, validators=[MinValueValidator(0)])
    date_of_transaction = models.DateTimeField(
        auto_now_add=True, editable=False)
    date_of_verification = models.DateTimeField(
        null=True, blank=True, editable=False)

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def save(self, *args, **kwargs):
        if not self.is_verified:
            self.to_be_verified_by.email_user(
                "New transaction", "Verify the transaction!", settings.EMAIL_HOST)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.diney.username} needs to give {self.amount} to {self.liney.username}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='to_be_verified_users', null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email}--{self.token}"


# personal expense tracker
class Expense(models.Model):
    type = models.CharField(max_length=10,default='E', editable=False)
    CATEGORIES = (
        ('Food', 'Food'),
        ('Beverage', 'Beverage'),
        ('Lend/Borrow', 'Lend/Borrow'),
        ('Entertainment', 'Entertainment'),
        ('Utility', 'Utitity'),
        ('Other', 'Other')
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="expenses", editable=False)
    amount = models.DecimalField(
        max_digits=20, decimal_places=3, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False)
    category = models.CharField(max_length=15, choices=CATEGORIES)
    description = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return f"{self.amount} on {self.created_at}"


class Income(models.Model):
    type = models.CharField(max_length=10, default='I', editable=False)
    CATEGORIES = (
        ('Salary', 'Salary'),
        ('Bonus', 'Bonus'),
        ('Commission', 'Commission'),
        ('Other', 'Other')
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="incomes", editable=False)
    amount = models.DecimalField(
        max_digits=20, decimal_places=3, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False)
    category = models.CharField(max_length=15, choices=CATEGORIES)
    description = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return f"{self.amount} on {self.created_at}"
