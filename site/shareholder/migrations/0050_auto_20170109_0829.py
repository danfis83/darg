# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-09 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholder', '0049_auto_20170106_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='company_department',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='optiontransaction',
            name='registration_type',
            field=models.CharField(blank=True, choices=[(b'1', 'Eigenbestand'), (b'2', 'Eigene Rechnung')], max_length=1, null=True, verbose_name='Wertpapiererwerb f\xfcr ...'),
        ),
        migrations.AlterField(
            model_name='position',
            name='is_split',
            field=models.BooleanField(default=False, verbose_name='Transaktion ist Teil eines Aktiensplits'),
        ),
        migrations.AlterField(
            model_name='position',
            name='registration_type',
            field=models.CharField(blank=True, choices=[(b'1', 'Eigenbestand'), (b'2', 'Eigene Rechnung')], max_length=1, null=True, verbose_name='Wertpapiererwerb f\xfcr ...'),
        ),
    ]
