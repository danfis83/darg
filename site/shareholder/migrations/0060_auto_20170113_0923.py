# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-13 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shareholder', '0059_auto_20161119_1150'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name', 'iso_code'], 'verbose_name': 'Land', 'verbose_name_plural': 'Countries'},
        ),
        migrations.AddField(
            model_name='company',
            name='c_o',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='C/O'),
        ),
        migrations.AddField(
            model_name='company',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='company',
            name='pobox',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='PO Box'),
        ),
        migrations.AddField(
            model_name='company',
            name='postal_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Postal code'),
        ),
        migrations.AddField(
            model_name='company',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Province'),
        ),
        migrations.AddField(
            model_name='company',
            name='street',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Street'),
        ),
        migrations.AddField(
            model_name='company',
            name='street2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Street 2'),
        ),
        migrations.AlterField(
            model_name='company',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shareholder.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='optiontransaction',
            name='depot_type',
            field=models.CharField(blank=True, choices=[(b'0', 'Zertifikatsdepot'), (b'1', 'Gesellschaftsdepot'), (b'2', 'Sperrdepot')], max_length=1, null=True, verbose_name='In welcher Depotart wird das Wertpapier gespeichert.'),
        ),
        migrations.AlterField(
            model_name='position',
            name='depot_type',
            field=models.CharField(blank=True, choices=[(b'0', 'Zertifikatsdepot'), (b'1', 'Gesellschaftsdepot'), (b'2', 'Sperrdepot')], max_length=1, null=True, verbose_name='In welcher Depotart wird das Wertpapier gespeichert.'),
        ),
        migrations.AlterField(
            model_name='security',
            name='cusip',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\xd6ffentliche Wertpapiernummer aka Valor, WKN, CUSIP: http://bit.ly/2ieXwuK'),
        ),
        migrations.AlterField(
            model_name='shareholderstatement',
            name='pdf_file',
            field=models.FilePathField(match=b'.+\\.pdf', max_length=500, path=b'/home/daniel/workspace/patroqueeet/darg/site/media_restricted/shareholder/statements', recursive=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='c_o',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='C/O'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shareholder.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pobox',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='PO Box'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Postal code'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Province'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='street',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Street'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='street2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Street 2'),
        ),
    ]
