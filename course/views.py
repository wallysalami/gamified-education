from functools import reduce

from django.contrib.auth.views import login as contrib_login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Case, When, F, Q, IntegerField, ExpressionWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rank import DenseRank, UpperRank, Rank

from django.utils.timezone import get_default_timezone

from .models import *


def error_page(request):
    return render(
        request,
        'course/error_page.html',
        {
            'request': request
        }
    )


def index(request):
    return redirect('/login/')
    
    
def login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect('/courses')
    else:
        return contrib_login(request, **kwargs)


@login_required(login_url='/login/')
def courses(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        enrollments = student.enrollment_set.all()
    elif hasattr(request.user, 'instructor'):
        instructor = request.user.instructor
        enrollments = instructor.classinstructor_set.all()
    else:
        enrollments = []
    
    if len(enrollments) == 1:
        enrollment = enrollments[0]
        return redirect('/%s/%s/assignments' %(enrollment.course_class.course.code, enrollment.course_class.code))
    else:
        return render(
            request,
            'course/courses.html',
            {
                'enrollments': enrollments
            }
        )


@login_required(login_url='/login/')
def course_class(request, course_code, class_code):
    try:
        enrollment = get_enrollment(request.user.id, course_code, class_code)
        course_class = enrollment.course_class
        student_id = enrollment.student_id
    except ObjectDoesNotExist:
        try:
            class_instructor = get_class_instructor(request, course_code, class_code)
            course_class = class_instructor.course_class
            student_id = None
        except ObjectDoesNotExist:
            raise Http404("Student/instructor not found")
    
    ranking = get_ranking_data(course_class, course_class.ranking_size)

    posts = Post.objects.filter(
        course_class=course_class
    ).order_by(
        '-is_pinned_to_the_top', '-post_datetime'
    ).all()

    return render(
        request,
        'course/class.html',
        {
            'active_tab': 'class',
            'course_class': course_class,
            'ranking': ranking,
            'student_id': student_id,
            'posts': posts
        }
    )


@login_required(login_url='/login/')
def assignments (request, course_code, class_code, student_id=None):
    try:
        enrollment = get_enrollment(request.user.id, course_code, class_code)
        course_class = enrollment.course_class
        students_data = None
    except ObjectDoesNotExist:
        try:
            class_instructor = get_class_instructor(request, course_code, class_code)
            course_class = class_instructor.course_class
            students_data = get_students_data(course_class)
            try:
                enrollment = Enrollment.objects.get(student_id=student_id, course_class=course_class)
            except ObjectDoesNotExist:
                enrollment = None
                
        except ObjectDoesNotExist:
            raise Http404("Student/instructor not found")
    
    return render(
        request,
        'course/assignments.html',
        {
            'active_tab': 'assignments',
            'course_class': course_class,
            'enrollment': enrollment,
            'assignment_items_data': assignment_items_data(enrollment),
            'students_data': students_data,
            'student_id': student_id
        }
    )


def get_enrollment(student_user_id, course_code, class_code):
    student = Student.objects.get(user_id=student_user_id)
    course = Course.objects.get(code=course_code)
    course_class = CourseClass.objects.get(course=course, code=class_code)
    enrollment = Enrollment.objects.get(student=student, course_class=course_class)

    return enrollment
    
def get_class_instructor(request, course_code, class_code):
    instructor = Instructor.objects.get(user_id=request.user.id)
    course = Course.objects.get(code=course_code)
    course_class = CourseClass.objects.get(course=course, code=class_code)
    class_instructor = ClassInstructor.objects.get(instructor=instructor, course_class=course_class)

    return class_instructor
    
def get_ranking_data(course_class, ranking_size):
    ranking = Grade.objects.values(
        'enrollment__student__id'
    ).annotate(
        total = Sum(
            Case(
                When(is_canceled=True, then=0),
                default=F('percentage')
            ) * F('assignment_task__points'), 
            output_field=IntegerField()
        ),
        full_name = F('enrollment__student__full_name'),
        student_id = F('enrollment__student__id'),
    ).annotate( 
        # this "dense_rank" was throwing an error sometimes, randomly
        # it was not finding the previous "total" annotation
        # so I put it in another "annotate" to respect the dependency
        dense_rank = Rank('total'),
    ).filter(
        enrollment__course_class = course_class
    ).order_by('-total', 'full_name')[:ranking_size]
    # print(ranking.query)
    
    return ranking
    
def get_students_data(course_class):
    return Student.objects.values(
        'id',
        'full_name'
    ).filter(
        enrollment__course_class = course_class
    ).order_by('full_name')

def assignment_items_data(enrollment):
    if enrollment == None:
        return None
    
    points_data = []
    assignments = enrollment.course_class.course.assignment_set.order_by('id').all()
    for assignment in assignments:
        assignment_data = {}
        assignment_data['name'] = assignment.name
        assignment_data['description'] = assignment.description

        tasks_data = assignment_tasks_data(assignment, enrollment)
        
        is_there_any_task_to_show = reduce(lambda x, y: True if not y['is_optional'] or y['grade_percentage'] != None else x, tasks_data, False)
        if not is_there_any_task_to_show:
            continue

        are_all_tasks_optional = reduce(lambda x, y: False if not y['is_optional'] else x, tasks_data, True)
        if are_all_tasks_optional:
            total_task_points = reduce(lambda x, y: x + y['task_points'], tasks_data, 0)
        else:
            total_task_points = reduce(lambda x, y: x+(y['task_points'] if not y['is_optional'] else 0), tasks_data, 0)
        
        total_grade_points = reduce(lambda x, y: x+y['grade_points'] if not y['grade_is_canceled'] else x, tasks_data, 0)
        
        assignment_data['tasks'] = tasks_data
        assignment_data['total_task_points'] = total_task_points
        assignment_data['total_grade_points'] = total_grade_points
        if total_task_points == 0:
            assignment_data['total_grade_percentage'] = 0
        else:
            assignment_data['total_grade_percentage'] = round(total_grade_points / total_task_points * 100)
        
        points_data.append(assignment_data)

    return points_data

def assignment_tasks_data(assignment, enrollment):
    tasks_data = []
    for assignment_task in assignment.ordered_assignment_tasks():
        task_data = {}
        task_data['name'] = assignment_task.task.name
        task_data['task_points'] = assignment_task.points
        task_data['is_optional'] = assignment_task.is_optional
        grade = assignment_task.grade_set.all().filter(enrollment=enrollment).first()
        if grade != None:
            task_data['grade_percentage'] = round(grade.percentage * 100)
            task_data['grade_points'] = round(task_data['task_points'] * grade.percentage)
            task_data['grade_is_canceled'] = grade.is_canceled
        else:
            task_data['grade_percentage'] = None
            task_data['grade_points'] = 0
            task_data['grade_is_canceled'] = False
        
        tasks_data.append(task_data)
    
    return tasks_data