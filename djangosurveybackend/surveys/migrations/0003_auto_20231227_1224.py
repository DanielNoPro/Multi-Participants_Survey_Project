# Generated by Django 3.2.23 on 2023-12-27 05:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('surveys', '0002_auto_20231221_2108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('-answered_at',)},
        ),
        migrations.AlterModelOptions(
            name='participantsurvey',
            options={'ordering': ('-participant_joined_at',)},
        ),
        migrations.AlterModelOptions(
            name='surveyquestion',
            options={'ordering': ('-asked_at',)},
        ),
        migrations.AlterField(
            model_name='question',
            name='question_created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_type', to='surveys.questiontype'),
        ),
        migrations.AlterField(
            model_name='questionoption',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='surveys.question'),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('question', 'survey', 'option', 'answered_by')},
        ),
        migrations.AlterUniqueTogether(
            name='participantsurvey',
            unique_together={('participant', 'survey')},
        ),
        migrations.AlterUniqueTogether(
            name='surveyquestion',
            unique_together={('question', 'survey', 'asked_by')},
        ),
    ]
