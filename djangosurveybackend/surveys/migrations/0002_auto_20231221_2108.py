# Generated by Django 3.2.23 on 2023-12-21 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="survey",
            name="end_date",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="survey",
            name="start_date",
            field=models.DateTimeField(),
        ),
    ]
