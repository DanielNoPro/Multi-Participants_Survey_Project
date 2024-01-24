# Generated by Django 3.2.23 on 2024-01-06 16:37

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('surveys', '0004_loadmasterdata'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('question', 'survey', 'option', 'answered_by', 'answered_at')},
        ),
    ]
