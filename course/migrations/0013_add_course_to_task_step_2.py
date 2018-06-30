# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def add_course_to_tasks(apps, schema_editor):
    Task = apps.get_model('course', 'Task')
    AssignmentTask = apps.get_model('course', 'AssignmentTask')
    for task in Task.objects.all():
        for assignment_task in AssignmentTask.objects.filter(task=task).all():
            if task.course == None:
                task.course = assignment_task.assignment.course
                task.save()
            elif task.course != assignment_task.assignment.course:
                other_task = Task.objects.filter(
                    name=task.name,
                    course=assignment_task.assignment.course
                ).first()
                if other_task == None:
                    other_task = Task.objects.create(
                        course_id=assignment_task.assignment.course_id,
                        name=task.name, description=task.description
                    )

                assignment_task.task = other_task
                assignment_task.save()

    Task.objects.filter(course=None).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('course', '0012_add_course_to_task_step_1'),
    ]
    
    operations = [
        migrations.RunPython(add_course_to_tasks),
    ]
