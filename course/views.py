from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Student, Course, CourseClass, Enrollment

def index(request):
    return redirect('/login/')


@login_required
def courses(request):
    student = request.user.student
    # course_class = CourseClass.objects.filter() request.user
    return HttpResponse("%s!" % student.full_name)


@login_required
def course_class(request, course_code):
    enrollment = get_enrollment(request, course_code)
    return HttpResponse("%s page!" % enrollment.course_class)


@login_required
def me (request, course_code):
    enrollment = get_enrollment(request, course_code)
    return HttpResponse("%s page for %s!" % (enrollment.course_class, enrollment.student.full_name))


def get_enrollment(request, course_code):
    student = get_object_or_404(Student, user_id=request.user.id)
    course = get_object_or_404(Course, code=course_code)
    class_ids = CourseClass.objects.filter(course=course).values_list('id', flat=True)
    enrollment = get_object_or_404(Enrollment, student=student, course_class_id__in=class_ids)

    return enrollment