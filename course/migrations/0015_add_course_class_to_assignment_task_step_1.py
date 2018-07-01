# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('course', '0014_add_course_to_task_step_3'),
    ]
    
    operations = [
        migrations.RemoveField(
            model_name='Assignment',
            name='enabled_from',
        ),
        migrations.RemoveField(
            model_name='Assignment',
            name='enabled_until',
        ),
        migrations.AddField(
            model_name='AssignmentTask',
            name='course_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course.CourseClass'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='AssignmentTask',
            unique_together=set([('assignment', 'task', 'course_class')]),
        ),
    ]
