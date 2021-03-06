# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-19 13:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0004_ranking-size'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassInstructor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.CourseClass')),
            ],
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='classinstructor',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Instructor'),
        ),
        migrations.AlterUniqueTogether(
            name='classinstructor',
            unique_together=set([('instructor', 'course_class')]),
        ),
    ]
