# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('body', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=140)),
                ('created_date', models.DateField(auto_now=True, auto_now_add=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('completed', models.BooleanField(default=None)),
                ('completed_date', models.DateField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('priority', models.PositiveIntegerField(max_length=3)),
                ('assigned_to', models.ForeignKey(related_name='todo_assigned_to', to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE)),
                ('created_by', models.ForeignKey(related_name='todo_created_by', to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['priority'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('slug', models.SlugField(max_length=60, editable=False)),
                ('group', models.ForeignKey(to='auth.Group', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Lists',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together=set([('group', 'slug')]),
        ),
        migrations.AddField(
            model_name='item',
            name='list',
            field=models.ForeignKey(to='todo.List', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='task',
            field=models.ForeignKey(to='todo.Item', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
