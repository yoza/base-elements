# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-07 16:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0003_auto_20151214_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparams',
            name='slogan',
            field=models.CharField(blank=True, help_text='Put here text for site slogan', max_length=512, null=True, verbose_name='Site slogan'),
        ),
    ]
