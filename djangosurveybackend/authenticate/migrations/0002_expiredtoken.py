# Generated by Django 3.2.23 on 2023-12-29 11:48

import django.db.models.deletion
from django.db import migrations, models

import authenticate.models


class Migration(migrations.Migration):
    dependencies = [
        ("authtoken", "0003_tokenproxy"),
        ("authenticate", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExpiredToken",
            fields=[
                (
                    "token_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="authtoken.token",
                    ),
                ),
                (
                    "expired",
                    models.DateTimeField(
                        default=authenticate.models.get_expired_default_time
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Expired Tokens",
            },
            bases=("authtoken.token",),
        ),
    ]
