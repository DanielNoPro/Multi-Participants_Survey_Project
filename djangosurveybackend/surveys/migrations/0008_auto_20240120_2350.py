# Generated by Django 3.2.23 on 2024-01-20 16:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0007_create_get_survey_answer_statistics_by_user_function"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="participantsurvey",
            options={
                "ordering": ("-participant_joined_at",),
                "verbose_name_plural": "Participant Surveys",
            },
        ),
        migrations.AlterModelOptions(
            name="questiontype",
            options={"verbose_name_plural": "Question Types"},
        ),
        migrations.AddField(
            model_name="question",
            name="is_deletable",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="question",
            name="is_editable",
            field=models.BooleanField(default=True),
        ),
    ]
