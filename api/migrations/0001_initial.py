# Generated by Django 4.1.6 on 2023-02-20 19:13

import api.managers
from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, unique=True, verbose_name='email address')),
                ('username', models.CharField(default='', editable=False, max_length=20)),
                ('first_name', models.CharField(blank=True, max_length=20, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=20, verbose_name='last name')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('friend_requests', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, default=list, null=True, size=None)),
                ('friends', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, default=list, null=True, size=None)),
                ('sent_friend_requests', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, default=list, null=True, size=None)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', api.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('C', 'Credit'), ('D', 'Debit')], max_length=10)),
                ('transaction_detail', models.CharField(max_length=120)),
                ('is_verified', models.BooleanField(default=False, editable=False)),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('date_of_transaction', models.DateTimeField(auto_now_add=True)),
                ('date_of_verification', models.DateTimeField(blank=True, editable=False, null=True)),
                ('diney', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='debit_transactions', to=settings.AUTH_USER_MODEL)),
                ('liney', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='credit_transactions', to=settings.AUTH_USER_MODEL)),
                ('to_be_verified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions_to_be_verified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
            },
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
