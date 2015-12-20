# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-15 01:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0002_auto_20151214_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparams',
            name='description',
            field=models.TextField(blank=True, help_text='Site Description', null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='siteparams',
            name='footer',
            field=models.CharField(blank=True, help_text='Site copyright', max_length=512, null=True, verbose_name='copyright'),
        ),
        migrations.AddField(
            model_name='siteparams',
            name='mdescrip',
            field=models.TextField(blank=True, help_text='The site meta description', null=True, verbose_name='Meta description'),
        ),
        migrations.AddField(
            model_name='siteparams',
            name='title',
            field=models.CharField(blank=True, help_text='Put here alternative text for logo image and site name', max_length=512, null=True, verbose_name='Site title'),
        ),
    ]
