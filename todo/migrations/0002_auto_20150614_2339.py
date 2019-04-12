# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("todo", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="item", name="created_date", field=models.DateField(auto_now=True)
        ),
        migrations.AlterField(
            model_name="item", name="priority", field=models.PositiveIntegerField()
        ),
    ]
