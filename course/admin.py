from django.contrib import admin
from django.apps import apps
from .models import *

# app = apps.get_app_config('course')

# for model_name, model in app.models.items():
#     admin.site.register(model)

class BasicAdmin(admin.ModelAdmin):
    class Media:
        css = { "all" : ("course/admin.css",) }


class CourseAdmin(BasicAdmin):
    list_display = ('name', 'code', 'description')
    ordering = ('name',)

admin.site.register(Course, CourseAdmin)


class CourseClassAdmin(BasicAdmin):
    list_display = ('code', 'start_date', 'end_date')
    ordering = ('start_date', 'code',)

admin.site.register(CourseClass, CourseClassAdmin)


class TaskAdmin(BasicAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)

admin.site.register(Task, TaskAdmin)


class AssignmentTaskInline(admin.TabularInline):
    model = AssignmentTask
    extra = 1
    ordering = ('id',)

class AssignmentAdmin(BasicAdmin):
    inlines = [AssignmentTaskInline]
    list_display = ('name', 'description')
    ordering = ('name',)

admin.site.register(Assignment, AssignmentAdmin)


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1
    ordering = ('id',)
    
class AssignmentTaskAdmin(BasicAdmin):
    inlines = [GradeInline]
    # list_display = ('name', 'description')
    ordering = ('id',)

admin.site.register(AssignmentTask, AssignmentTaskAdmin)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    ordering = ('id',)


class StudentAdmin(BasicAdmin):
    inlines = [EnrollmentInline]
    list_display = ('full_name', 'id_number', 'enrollments')
    search_fields = ['full_name']
    ordering = ('full_name',)

admin.site.register(Student, StudentAdmin)