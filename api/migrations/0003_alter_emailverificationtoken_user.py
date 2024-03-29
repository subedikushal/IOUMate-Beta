# Generated by Django 4.1.6 on 2023-02-20 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_user_is_email_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverificationtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_be_verified_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
