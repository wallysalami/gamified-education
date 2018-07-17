# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('course', '0013_add_course_to_task_step_2'),
    ]
    
    operations = [
        migrations.AlterField(
            model_name='task',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course'),
            preserve_default=False,
        ),
    ]
