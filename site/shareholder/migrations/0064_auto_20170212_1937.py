# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-02-12 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholder', '0063_auto_20170212_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='vesting_months',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='is_management',
            field=models.BooleanField(default=False, verbose_name='user is management/board member of company'),
        ),
    ]