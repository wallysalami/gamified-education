from django.core.management.base import BaseCommand
from datetime import date
from course.models import *

class Command(BaseCommand):
    help = 'Compute percentages for achievements in current course classes'

    def handle(self, *args, **options):
        today = date.today()
        course_classes = CourseClass.objects.filter(start_date__lte=today, end_date__gte=today)
        refresh_achievements(course_classes)

def refresh_achievements(course_classes):
    for course_class in course_classes:
        print("Refreshing achievements of %s" % course_class)
        
        for enrollment in course_class.enrollment_set.all():
            for class_badge in course_class.classbadge_set.all():
                percentages = []

                for class_badge_criteria in class_badge.classbadgecriteria_set.all():
                    result = 0.0
                    goal = class_badge_criteria.goal
                    goal_type_is_percentage = (class_badge_criteria.goal_type == ClassBadgeCriteria.PERCENTAGE)

                    assignment = class_badge_criteria.assignment
                    task = class_badge_criteria.task
                    assignment_tasks = AssignmentTask.objects.filter(course_class=course_class)

                    if assignment != None and task != None:
                        assignment_task = assignment_tasks.filter(assignment=assignment, task=task).first()
                        grade = Grade.objects.filter(enrollment=enrollment, assignment_task=assignment_task).first()

                        if grade == None:
                            result = 0
                        elif goal_type_is_percentage:
                            result = grade.score
                        else:
                            result = grade.points

                    elif assignment != None:
                        assignment_tasks = assignment_tasks.filter(assignment=assignment)

                        for assignment_task in assignment_tasks:
                            grade = Grade.objects.filter(enrollment=enrollment, assignment_task=assignment_task).first()
                            if grade != None:
                                result += grade.points

                        if goal_type_is_percentage:
                            points = assignment.points(course_class)
                            if points == 0:
                                continue
                            result = result / points

                    elif task != None:
                        assignment_tasks = assignment_tasks.filter(task=task)

                        total = 0.0
                        for assignment_task in assignment_tasks:
                            grade = Grade.objects.filter(enrollment=enrollment, assignment_task=assignment_task).first()
                            
                            if goal_type_is_percentage:
                                total += 1
                                if grade != None and grade.score == 1:
                                    result += 1
                            elif grade != None:
                                result += grade.points
                                    

                        if goal_type_is_percentage:
                            result = result / total

                    if not class_badge_criteria.accepts_partial_goal and result < class_badge_criteria.goal:
                        result = 0.0

                    percentage = result / goal
                    percentage = min(max(percentage, 0), 1)

                    percentages.append(percentage)
                    

                if percentages == []:
                    continue

                if class_badge.aggregation_type_for_criteria == ClassBadge.AND:
                    percentage = sum(percentages, 0.0) / len(percentages)
                else:
                    percentage = max(percentages)
                        
                achievement = Achievement.objects.filter(enrollment=enrollment, class_badge=class_badge).first()
                if achievement == None:
                    achievement = Achievement(enrollment=enrollment, class_badge=class_badge)
                achievement.percentage = percentage
                achievement.save()