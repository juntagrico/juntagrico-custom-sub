# Generated by Django 3.0.2 on 2020-04-08 20:56

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('juntagrico_custom_sub', '0010_generate_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(default='1', max_length=100, unique=True, validators=[
                django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'),
                                                      'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.',
                                                      'invalid')], verbose_name='Sortier-Code'),
        ),
    ]
