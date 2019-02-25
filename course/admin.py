from django.contrib import admin
from django.apps import apps
from .models import *
from .forms.forms import UserCreationForm, CaptchaPasswordResetForm
from django.forms import BaseInlineFormSet, ModelForm
from django.forms.widgets import TextInput
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ungettext
import markdown2

from django.utils.formats import date_format

def invite_user(modeladmin, request, queryset):
    for user in queryset:
        if user.has_usable_password():
            messages.error(
                request,
                _("User %(username)s already has a password!") % {'username': user.username}
            )
            return
        elif user.email == '':
            messages.error(
                request,
                _("User %(username)s has no email!") % {'username': user.username }
            )
            return

    for user in queryset:
        reset_form = CaptchaPasswordResetForm({'email': user.email})
        reset_form.is_valid()
        reset_form.save(
            request=request,
            use_https=request.is_secure(),
            subject_template_name='email/password_creation_subject.txt',
            html_email_template_name='email/password_creation_email.html',
        )

    success_message = ungettext(
        "%(count)d email sent successfully!",
        "%(count)d emails sent successfully!",
        queryset.count()
    )% {
        'count': queryset.count(),
    }
    messages.success(request, success_message)

invite_user.short_description = _("Send invitation to selected users")

def has_usable_password(self):
    return _( str( self.has_usable_password() ) )

has_usable_password.short_description = _('Has Password?')


def last_login_formatted(self):
    if self.last_login == None:
        return None
    return date_format(timezone.localtime(self.last_login), format='SHORT_DATETIME_FORMAT', use_l10n=True)

last_login_formatted.short_description = _('Last Login')


class UserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', has_usable_password, last_login_formatted)
    actions = (invite_user,)
    add_form = UserCreationForm
    list_filter = ('last_login', 'groups',)
    ordering = ('first_name', 'last_name')
    
    def save_model(self, request, obj, form, change):
        if not change and (not form.cleaned_data['password1'] or not obj.has_usable_password()):
            obj.set_unusable_password()

        super(UserAdmin, self).save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class BasicAdmin(admin.ModelAdmin):
    class Media:
        css = { "all" : ("course/admin.css",) }
        js = ["course/admin.js"]


class CourseForm(ModelForm):
    class Meta:
        model = CourseClass
        fields = '__all__'
        widgets = {
            'primary_hex_color': TextInput(attrs={'type': 'color'}),
            'secondary_hex_color': TextInput(attrs={'type': 'color'}),
        }

class CourseAdmin(BasicAdmin):
    form = CourseForm
    list_display = ('name', 'code', 'description')
    ordering = ('name',)

admin.site.register(Course, CourseAdmin)


def duplicate_course_class(modeladmin, request, queryset):
    for course_class in queryset:
        new_course_class = CourseClass.objects.get(pk=course_class.id)
        new_course_class.id = None
        
        # Duplicate course class, adding a (number) on the code
        copy_number = 2
        while True:
            new_code = "%s (%d)" % (course_class.code, copy_number)
            if CourseClass.objects.filter(code=new_code).first() == None:
                new_course_class.code = new_code
                break
            else:
                copy_number += 1
        new_course_class.save()
        
        # Duplicate assignment tasks from original course class
        existing_assignment_tasks = AssignmentTask.objects.filter(course_class=course_class)
        for existing_assignment_task in existing_assignment_tasks:
            new_assignment_task = existing_assignment_task
            new_assignment_task.id = None
            new_assignment_task.course_class = new_course_class
            new_assignment_task.save()
            
duplicate_course_class.short_description = _("Duplicate course class")

class CourseClassAdmin(BasicAdmin):
    list_display = ('code', 'course', 'start_date', 'end_date')
    ordering = ('-start_date', 'course', 'code')
    actions = (duplicate_course_class,)

admin.site.register(CourseClass, CourseClassAdmin)


class TaskAdmin(BasicAdmin):
    list_display = ('name', 'course', 'description')
    list_filter = ('course',)
    ordering = ('course', 'name',)

admin.site.register(Task, TaskAdmin)


class AssignmentTaskInline(admin.TabularInline):
    model = AssignmentTask
    extra = 1
    ordering = ('id',)

class AssignmentAdmin(BasicAdmin):
    inlines = [AssignmentTaskInline]
    list_display = ('name', 'course', 'description')
    list_filter = ('course',)
    ordering = ('name',)

admin.site.register(Assignment, AssignmentAdmin)


class GradeInlineFormSet(BaseInlineFormSet):
    model = Grade
    _enrollment_ids = None

    @property
    def enrollment_ids(self):
        if self.instance.assignment_id == None:
            return []
        if not self._enrollment_ids:
            self._enrollment_ids = list(Enrollment.objects.filter(
                course_class = self.instance.course_class
            ).order_by(
                'student__full_name'
            ).values_list('id', flat=True))
        return self._enrollment_ids

    def total_form_count(self):
        return len(self.enrollment_ids) if self.instance.id != None else 0

    def __init__(self, *args, **kwargs):
        super(GradeInlineFormSet, self).__init__(*args, **kwargs)            
        
        enrollment_ids = list(self.enrollment_ids) # make a copy of the list
        index = 0
        for form in self:
            if form.instance.id != None:
                if form.instance.enrollment.id in enrollment_ids:
                    enrollment_ids.remove(form.instance.enrollment.id)
            else:
                form.initial['enrollment'] = enrollment_ids[index]
                form.initial['percentage'] = ""
                index += 1


class GradeInline(admin.TabularInline):
    model = Grade
    ordering = ('enrollment__course_class__code', 'enrollment__student__full_name',)
    formset = GradeInlineFormSet
    raw_id_fields = ("enrollment",)
    
class AssignmentTaskAdmin(BasicAdmin):
    inlines = [GradeInline]
    list_display = ('__str__', 'course_class')
    list_filter = ('course_class',)
    ordering = ('-course_class', 'assignment_id', 'id',)

    def course(self, obj):
        return obj.assignment.course

admin.site.register(AssignmentTask, AssignmentTaskAdmin)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    ordering = ('id',)


class EnrollmentGradeInlineFormSet(BaseInlineFormSet):
    model = Grade
    _assignment_tasks_ids = None

    @property
    def assignment_task_ids(self):
        if self.instance.course_class_id == None:
            return []
        if not self._assignment_tasks_ids:
            self._assignment_tasks_ids = list(AssignmentTask.objects.filter(
                course_class = self.instance.course_class
            ).order_by(
                'assignment_id', 'id'
            ).values_list('id', flat=True))
        return self._assignment_tasks_ids

    def total_form_count(self):
        return len(self.assignment_task_ids) if self.instance.id != None else 0

    def __init__(self, *args, **kwargs):
        super(EnrollmentGradeInlineFormSet, self).__init__(*args, **kwargs)            
        
        assignment_task_ids = list(self.assignment_task_ids) # make a copy of the list
        index = 0
        for form in self:
            if form.instance.id != None:
                assignment_task_ids.remove(form.instance.assignment_task.id)
            else:
                form.initial['assignment_task'] = assignment_task_ids[index]
                form.initial['percentage'] = ""
                index += 1

class SimpleGradeInline(admin.TabularInline):
    model = Grade
    raw_id_fields = ("assignment_task",)
    formset = EnrollmentGradeInlineFormSet
    ordering = ('assignment_task__assignment_id', 'assignment_task')

class EnrollmentAdmin(BasicAdmin):
    inlines = [SimpleGradeInline]
    list_display = ('student', 'course_class')
    list_filter = ('course_class',)
    ordering = ('-course_class__start_date', 'student__full_name')
    search_fields = ('student__full_name',)
    

admin.site.register(Enrollment, EnrollmentAdmin)


class StudentAdmin(BasicAdmin):
    inlines = [EnrollmentInline]
    list_display = ('full_name', 'id_number', 'enrollments')
    search_fields = ('full_name',)
    ordering = ('full_name',)
    raw_id_fields = ("user",)

admin.site.register(Student, StudentAdmin)


class ClassInstructorInline(admin.TabularInline):
    model = ClassInstructor
    ordering = ('course_class_id',)


class InstructorAdmin(BasicAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)
    ordering = ('full_name',)
    inlines = [ClassInstructorInline]
    raw_id_fields = ('user',)

admin.site.register(Instructor, InstructorAdmin)


class PostAdmin(BasicAdmin):
    model = Post
    list_display = ('course_class', 'title','post_datetime')
    ordering = ('-post_datetime',)
    read_only = ('html_code')
    
    def save_model(self, request, post, form, change):
        post.html_code = markdown2.markdown(post.markdown_text, extras=["tables", "fenced-code-blocks"])
        super().save_model(request, post, form, change)
    
admin.site.register(Post, PostAdmin)


class WidgetAdmin(BasicAdmin):
    model = Widget
    list_display = ('course_class', 'title', 'order')
    ordering = ('order',)
    read_only = ('html_code')
    
    def save_model(self, request, post, form, change):
        post.html_code = markdown2.markdown(post.markdown_text, extras=["tables", "fenced-code-blocks"])
        super().save_model(request, post, form, change)
    
admin.site.register(Widget, WidgetAdmin)

class BadgeAdmin(BasicAdmin):
    model = Badge
    list_display = ('name', 'course')
    ordering = ('course', 'name')
    
admin.site.register(Badge, BadgeAdmin)


class AchievementInlineFormSet(BaseInlineFormSet):
    model = Achievement
    _enrollment_ids = None

    @property
    def enrollment_ids(self):
        if self.instance.badge_id == None:
            return []
        if not self._enrollment_ids:
            self._enrollment_ids = list(Enrollment.objects.filter(
                course_class = self.instance.course_class
            ).order_by(
                'student__full_name'
            ).values_list('id', flat=True))
        return self._enrollment_ids

    def total_form_count(self):
        return len(self.enrollment_ids) if self.instance.id != None else 0

    def __init__(self, *args, **kwargs):
        super(AchievementInlineFormSet, self).__init__(*args, **kwargs)            
        
        enrollment_ids = list(self.enrollment_ids) # make a copy of the list
        index = 0
        for form in self:
            if form.instance.id != None:
                if form.instance.enrollment.id in enrollment_ids:
                    enrollment_ids.remove(form.instance.enrollment.id)
            else:
                form.initial['enrollment'] = enrollment_ids[index]
                form.initial['percentage'] = ""
                index += 1

class AchievementInline(admin.TabularInline):
    model = Achievement
    ordering = ('enrollment__student__full_name',)
    formset = AchievementInlineFormSet
    raw_id_fields = ("enrollment",)


class ClassBadgeAdmin(BasicAdmin):
    model = ClassBadge
    list_display = ('badge', 'course_class')
    ordering = ('course_class', 'id')
    inlines = [AchievementInline]
    list_filter = ('course_class',)
    
admin.site.register(ClassBadge, ClassBadgeAdmin)