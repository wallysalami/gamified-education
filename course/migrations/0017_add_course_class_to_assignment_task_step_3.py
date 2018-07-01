# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('course', '0016_add_course_class_to_assignment_task_step_2'),
    ]
    
    operations = [
        migrations.AlterField(
            model_name='AssignmentTask',
            name='course_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.CourseClass'),
            preserve_default=False,
        ),
    ]
