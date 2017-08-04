# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 18:36
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('enabled_from', models.DateField(blank=True, null=True)),
                ('enabled_until', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Assignment')),
            ],
            options={
                'verbose_name': 'Assignment Task',
                'verbose_name_plural': 'Assignment Tasks',
                'db_table': 'course_assignment_task',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('description', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CourseClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course')),
            ],
            options={
                'verbose_name_plural': 'Classes',
                'db_table': 'course_class',
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.CourseClass')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('assignment_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.AssignmentTask')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Enrollment')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=200)),
                ('id_number', models.CharField(blank=True, max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('enabled_from', models.DateField(blank=True, null=True)),
                ('enabled_until', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Student'),
        ),
        migrations.AddField(
            model_name='assignmenttask',
            name='enrollments',
            field=models.ManyToManyField(through='course.Grade', to='course.Enrollment'),
        ),
        migrations.AddField(
            model_name='assignmenttask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Task'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course'),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('enrollment', 'assignment_task')]),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set([('student', 'course_class')]),
        ),
        migrations.AlterUniqueTogether(
            name='courseclass',
            unique_together=set([('code', 'course')]),
        ),
        migrations.AlterUniqueTogether(
            name='assignmenttask',
            unique_together=set([('assignment', 'task')]),
        ),
    ]
