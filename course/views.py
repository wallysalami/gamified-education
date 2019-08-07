import datetime
from functools import reduce
from django.contrib.auth.views import login as contrib_login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Case, When, F, Q, IntegerField, ExpressionWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
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
        return redirect('/classes/')
    else:
        email_info = {
            'is_email_configured': settings.EMAIL_HOST != ''
        }
        return contrib_login(request, extra_context=email_info, **kwargs)


@login_required(login_url='/login/')
def classes(request):
    today = datetime.date.today()
    if hasattr(request.user, 'student'):
        student = request.user.student
        all_classes = CourseClass.objects.filter(
            enrollment__student=student
        )
    elif hasattr(request.user, 'instructor'):
        instructor = request.user.instructor
        all_classes = CourseClass.objects.filter(
            classinstructor__instructor=instructor
        )
    else:
        all_classes = CourseClass.objects.none()
    
    if len(all_classes) == 1:
        course_class = all_classes[0]
        return redirect('/%s/%s/' %(course_class.course.code, course_class.code))
    else:
        return render(
            request,
            'course/classes.html',
            {
                'past_classes': filter_past_classes(all_classes),
                'current_classes': filter_current_classes(all_classes),
                'future_classes': filter_future_classes(all_classes),
            }
        )


@login_required(login_url='/login/')
def home(request, course_code, class_code):
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
    )

    widgets = Widget.objects.filter(
        course_class=course_class
    ).order_by('order')
    
    if hasattr(request.user, 'student'):
        posts = posts.filter(
            post_datetime__lte=datetime.datetime.now(),
            is_draft=False,
        )
    
    return render(
        request,
        'course/class.html',
        {
            'active_tab': 'home',
            'course_class': course_class,
            'ranking_size': course_class.ranking_size,
            'ranking': ranking,
            'student_id': student_id,
            'posts': posts,
            'widgets': widgets
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
            'assignment_items_data': get_assignments_data(enrollment),
            'achievements_data': get_achievements_data(enrollment),
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

def filter_past_classes(query):
    return query.filter(
        end_date__lt=datetime.date.today()
    ).order_by('-end_date', 'course__name', 'code').all()

def filter_current_classes(query):
    return query.filter(
        start_date__lte=datetime.date.today(),
        end_date__gte=datetime.date.today()
    ).order_by('start_date', 'course__name', 'code').all()

def filter_future_classes(query):
    return query.filter(
        start_date__gt=datetime.date.today()
    ).order_by('start_date', 'course__name', 'code').all()
    
def get_ranking_data(course_class, ranking_size):
    ranking = Grade.objects.values(
        'enrollment__student__id'
    ).annotate(
        total = Sum(
            Case(
                When(is_canceled=True, then=0),
                When(assignment_task__points=None, then=F('score')),
                default=F('score') * F('assignment_task__points'),
                output_field=IntegerField()
            )
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

def get_assignments_data(enrollment):
    if enrollment == None:
        return None
    
    points_data = []
    assignments = enrollment.course_class.course.assignment_set.order_by('id').all()
    for assignment in assignments:
        tasks_data = get_tasks_data(assignment, enrollment)
        
        if len(tasks_data) == 0:
            continue
        
        is_there_any_task_completed = reduce(
            lambda x, y: True if y['grade_points'] != None else x,
            tasks_data,
            False
        )
        if assignment.is_optional and not is_there_any_task_completed:
            continue

        are_all_tasks_optional = reduce(
            lambda x, y: False if not y['is_optional'] else x,
            tasks_data,
            True
        )
        if are_all_tasks_optional:
            total_task_points = None
        else:
            total_task_points = reduce(
                lambda x, y: x + (y['task_points'] if not y['is_optional'] and y['task_points'] != None else 0),
                tasks_data,
                0
            )
        
        if is_there_any_task_completed:
            total_grade_points = reduce(
                lambda x, y: x + y['grade_points'] if y['grade_points'] != None and not y['grade_is_canceled'] else x,
                tasks_data,
                0
            )
        else:
            total_grade_points = None
        
        if total_grade_points == None or total_task_points == None or total_task_points == 0:
            total_grade_percentage = None
        else:
            total_grade_percentage = round(total_grade_points / total_task_points * 100)

        assignment_data = {}
        assignment_data['name'] = assignment.name
        assignment_data['description'] = assignment.description
        assignment_data['tasks'] = tasks_data
        assignment_data['total_task_points'] = total_task_points
        assignment_data['total_grade_points'] = total_grade_points
        assignment_data['total_grade_percentage'] = total_grade_percentage
        
        points_data.append(assignment_data)

    return points_data

def get_tasks_data(assignment, enrollment):
    tasks_data = []
    for assignment_task in assignment.ordered_assignment_tasks(enrollment.course_class):
        grade = assignment_task.grade_set.all().filter(enrollment=enrollment).first()

        task_data = {}
        task_data['name'] = assignment_task.task.name
        task_data['task_points'] = assignment_task.points
        task_data['is_optional'] = assignment_task.is_optional
        if grade != None:
            task_data['grade_percentage'] = round(grade.score * 100) if assignment_task.points != None else None
            task_data['grade_points'] = grade.points
            task_data['grade_is_canceled'] = grade.is_canceled
        else:
            task_data['grade_percentage'] = None
            task_data['grade_points'] = None
            task_data['grade_is_canceled'] = False
        
        tasks_data.append(task_data)
    
    return tasks_data

def get_achievements_data(enrollment):
    if enrollment == None:
        return None
    
    achievements_data = []
    class_badges = enrollment.course_class.classbadge_set.order_by('id').all()
    for class_badge in class_badges:
        achievement = class_badge.achievement_set.filter(enrollment=enrollment).first()
        
        achievement_data = {}
        achievement_data['percentage'] = achievement.percentage if achievement != None else 0
        achievement_data['percentage_integer'] = int(achievement_data['percentage']*100)
        achievement_data['show_progress'] = class_badge.show_progress

        if class_badge.show_info_before_completion or achievement_data['percentage'] > 1:
            achievement_data['name'] = class_badge.badge.name
            achievement_data['description'] = class_badge.description
            achievement_data['icon'] = class_badge.badge.icon_url
        else:
            achievement_data['name'] = "???"
            achievement_data['description'] = _("(description will show up when you earn this badge)")
            achievement_data['icon'] = '/static/course/question-mark.svg'
        
        achievements_data.append(achievement_data)
        
    print(achievements_data)

    return achievements_data