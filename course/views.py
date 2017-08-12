from functools import reduce

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, IntegerField, ExpressionWrapper
from rank import DenseRank, UpperRank, Rank

from .models import AssignmentTask, Grade, Student, Course, CourseClass, Enrollment

def index(request):
    return redirect('/login/')


@login_required
def courses(request):
    student = request.user.student
    enrollments = student.enrollment_set.all()
    if len(enrollments) == 1:
        enrollment = enrollments[0]
        return redirect('/%s/%s/me' %(enrollment.course_class.course.code, enrollment.course_class.code))
    elif len(enrollments) == 0:
        return HttpResponse("(no course found)")
    else:
        return render(
            request,
            'course/courses.html',
            {
                'enrollments': enrollments
            }
        )


@login_required
def course_class(request, course_code, class_code):
    enrollment = get_enrollment(request, course_code, class_code)
    ranking = Grade.objects.values(
        'enrollment__student__id'
    ).annotate(
        total = Sum(
            F('percentage') * F('assignment_task__points'), 
            output_field=IntegerField()
        ),
        full_name = F('enrollment__student__full_name'),
        dense_rank = Rank('total'),
        student_id = F('enrollment__student__id'),
    ).filter(
        enrollment__course_class = enrollment.course_class
    ).order_by('-total', 'full_name')[:10]
    # print(ranking.query)

    return render(
        request,
        'course/class.html',
        {
            'active_tab': 'class',
            'course_class': enrollment.course_class,
            'ranking': ranking,
            'student_id': enrollment.student_id
        }
    )


@login_required
def me (request, course_code, class_code):
    enrollment = get_enrollment(request, course_code, class_code)
    print(assignment_items_data(enrollment))
    return render(
        request,
        'course/me.html',
        {
            'active_tab': 'me',
            'course_class': enrollment.course_class,
            'assignment_items_data': assignment_items_data(enrollment),
        }
    )


def get_enrollment(request, course_code, class_code):
    student = get_object_or_404(Student, user_id=request.user.id)
    course = get_object_or_404(Course, code=course_code)
    course_class = get_object_or_404(CourseClass, course=course, code=class_code)
    enrollment = get_object_or_404(Enrollment, student=student, course_class=course_class)

    return enrollment

def assignment_items_data(enrollment):
    points_data = []
    assignments = enrollment.course_class.course.assignment_set.order_by('id').all()
    for assignment in assignments:
        assignment_data = {}
        assignment_data['name'] = assignment.name
        assignment_data['description'] = assignment.description

        tasks_data = assignment_tasks_data(assignment, enrollment)

        total_task_points = reduce(lambda x, y: x+y['task_points'], tasks_data, 0)
        total_grade_points = reduce(lambda x, y: x+y['grade_points'], tasks_data, 0)
        
        assignment_data['tasks'] = tasks_data
        assignment_data['total_task_points'] = total_task_points
        assignment_data['total_grade_points'] = total_grade_points
        if total_task_points == 0:
            assignment_data['total_grade_percentage'] = 0
        else:
            assignment_data['total_grade_percentage'] = total_grade_points / total_task_points * 100
        
        points_data.append(assignment_data)

    return points_data

def assignment_tasks_data(assignment, enrollment):
    tasks_data = []
    for assignment_task in assignment.ordered_assignment_tasks():
        task_data = {}
        task_data['name'] = assignment_task.task.name
        task_data['task_points'] = assignment_task.points
        grade = assignment_task.grade_set.all().filter(enrollment=enrollment).first()
        if grade != None:
            task_data['grade_percentage'] = round(grade.percentage * 100)
            task_data['grade_points'] = round(task_data['task_points'] * grade.percentage)
        else:
            task_data['grade_percentage'] = None
            task_data['grade_points'] = 0
        
        tasks_data.append(task_data)
    
    return tasks_data