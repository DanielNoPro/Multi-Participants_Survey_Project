# Generated by Django 3.2.23 on 2023-12-30 04:00
import os

from django.core.management import call_command
from django.db import migrations

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filename = 'initial_data.json'


def load_fixture(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)
    call_command('loaddata', fixture_file)


class Migration(migrations.Migration):
    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]