# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-15 01:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='siteparams',
            table='elements_siteparam',
        ),
    ]
