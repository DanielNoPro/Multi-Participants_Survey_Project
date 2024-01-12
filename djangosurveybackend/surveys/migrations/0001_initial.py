# Generated by Django 3.2.23 on 2023-12-17 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantSurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=55)),
                ('is_active', models.BooleanField(default=True)),
                ('invited_participant_at', models.DateTimeField(auto_now_add=True)),
                ('participant_joined_at', models.DateTimeField(auto_now=True)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('question_created_at', models.DateTimeField(auto_now_add=True)),
                ('question_updated_at', models.DateTimeField(auto_now=True)),
                ('question_created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Questions',
                'ordering': ('-question_created_at',),
            },
        ),
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'QuestionTypes',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('survey_created_at', models.DateTimeField(auto_now_add=True)),
                ('survey_updated_at', models.DateTimeField(auto_now=True)),
                ('participant', models.ManyToManyField(through='surveys.ParticipantSurvey', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Surveys',
                'ordering': ('-survey_created_at',),
            },
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('asked_at', models.DateTimeField(auto_now_add=True)),
                ('adjusted_at', models.DateTimeField(auto_now=True)),
                ('asked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.question')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
        ),
        migrations.AddField(
            model_name='survey',
            name='questions',
            field=models.ManyToManyField(through='surveys.SurveyQuestion', to='surveys.Question'),
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('option_created_at', models.DateTimeField(auto_now_add=True)),
                ('option_updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.question')),
            ],
            options={
                'verbose_name_plural': 'QuestionOptions',
                'ordering': ('-option_created_at',),
            },
        ),
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.questiontype'),
        ),
        migrations.AddField(
            model_name='participantsurvey',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey'),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(null=True)),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('answer_updated_at', models.DateTimeField(auto_now=True)),
                ('answered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='surveys.questionoption')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.question')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.survey')),
            ],
            options={
                'verbose_name_plural': 'Questions',
                'ordering': ('-answered_at',),
            },
        ),
    ]
