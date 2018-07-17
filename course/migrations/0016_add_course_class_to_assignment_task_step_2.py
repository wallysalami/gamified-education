# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def add_course_class_to_assigment_tasks(apps, schema_editor):
    AssignmentTask = apps.get_model('course', 'AssignmentTask')
    Grade = apps.get_model('course', 'Grade')
    
    for assignment_task in AssignmentTask.objects.order_by('id').all():
        for grade in Grade.objects.filter(assignment_task=assignment_task).all():
            if assignment_task.course_class == None:
                assignment_task.course_class = grade.enrollment.course_class
                assignment_task.save()
            elif assignment_task.course_class != grade.enrollment.course_class:
                other_assignment_task = AssignmentTask.objects.filter(
                    assignment=assignment_task.assignment,
                    task=assignment_task.task,
                    course_class=grade.enrollment.course_class
                ).first()
                if other_assignment_task == None:
                    other_assignment_task = AssignmentTask.objects.get(pk=assignment_task.id)
                    other_assignment_task.course_class = grade.enrollment.course_class
                    other_assignment_task.pk = None
                    other_assignment_task.save()

                grade.assignment_task = other_assignment_task
                grade.save()

    AssignmentTask.objects.filter(course_class=None).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('course', '0015_add_course_class_to_assignment_task_step_1'),
    ]
    
    operations = [
        migrations.RunPython(add_course_class_to_assigment_tasks),
    ]
