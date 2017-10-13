from django.contrib import admin
from django.apps import apps
from .models import *
from django.forms import BaseInlineFormSet
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# app = apps.get_app_config('course')

# for model_name, model in app.models.items():
#     admin.site.register(model)

UserAdmin.list_display = ('email', 'first_name', 'last_name', 'last_login')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class BasicAdmin(admin.ModelAdmin):
    class Media:
        css = { "all" : ("course/admin.css",) }


class CourseAdmin(BasicAdmin):
    icon = '<i class="material-icons">class</i>'
    list_display = ('name', 'code', 'description')
    ordering = ('name',)

admin.site.register(Course, CourseAdmin)


class CourseClassAdmin(BasicAdmin):
    icon = '<i class="material-icons">people</i>'
    list_display = ('code', 'start_date', 'end_date')
    ordering = ('start_date', 'code',)

admin.site.register(CourseClass, CourseClassAdmin)


class TaskAdmin(BasicAdmin):
    icon = '<i class="material-icons">list</i>'
    list_display = ('name', 'description')
    ordering = ('name',)

admin.site.register(Task, TaskAdmin)


class AssignmentTaskInline(admin.TabularInline):
    model = AssignmentTask
    extra = 1
    ordering = ('id',)

class AssignmentAdmin(BasicAdmin):
    icon = '<i class="material-icons">assignment</i>'
    inlines = [AssignmentTaskInline]
    list_display = ('name', 'description')
    ordering = ('name',)

admin.site.register(Assignment, AssignmentAdmin)


class GradeInlineFormSet(BaseInlineFormSet):
    model = Grade
    _enrollment_ids = None

    @property
    def enrollment_ids(self):
        if not self._enrollment_ids:
            self._enrollment_ids = list(Enrollment.objects.filter(
                course_class__course = self.instance.assignment.course
            ).order_by(
                'course_class__code', 'student__full_name'
            ).values_list('id', flat=True))
        return self._enrollment_ids

    def total_form_count(self):
        return len(self.enrollment_ids)

    def __init__(self, *args, **kwargs):
        super(GradeInlineFormSet, self).__init__(*args, **kwargs)            
        
        enrollment_ids = self.enrollment_ids
        index = 0
        for form in self:
            print(form.instance.id)
            if form.instance.id != None:
                enrollment_ids.remove(form.instance.enrollment.id)
            else:
                form.initial['enrollment'] = enrollment_ids[index]
                form.initial['percentage'] = ""
                index += 1


class GradeInline(admin.TabularInline):
    model = Grade
    ordering = ('enrollment__course_class__code', 'enrollment__student__full_name',)
    formset = GradeInlineFormSet
    
class AssignmentTaskAdmin(BasicAdmin):
    icon = '<i class="material-icons">playlist_add_check</i>'
    inlines = [GradeInline]
    # list_display = ('name', 'description')
    ordering = ('assignment_id','id',)

admin.site.register(AssignmentTask, AssignmentTaskAdmin)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    ordering = ('id',)


class SimpleGradeInline(admin.TabularInline):
    model = Grade

class EnrollmentAdmin(BasicAdmin):
    icon = '<i class="material-icons">person</i>'
    inlines = [SimpleGradeInline]
    list_display = ('student', 'course_class')
    ordering = ('course_class__code', 'student__full_name',)

admin.site.register(Enrollment, EnrollmentAdmin)


class StudentAdmin(BasicAdmin):
    icon = '<i class="material-icons">person</i>'
    inlines = [EnrollmentInline]
    list_display = ('full_name', 'id_number', 'enrollments')
    search_fields = ['full_name']
    ordering = ('full_name',)

admin.site.register(Student, StudentAdmin)