from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.db.models import Sum, F, IntegerField, Case, When
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.conf import settings

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100, blank=True)
    icon_file_name = models.ImageField(blank=True)
    icon_external_url = models.URLField(max_length=2000, blank=True)
    
    def __str__(self):
        return self.code + ' – ' + self.name

    @property
    def icon_url(self):
        if self.icon_file_name != '':
            return settings.MEDIA_URL + str(self.icon_file_name)
        elif self.icon_external_url != '':
            return self.icon_external_url
        else:
            # icon from https://pixabay.com/p-2268948/?no_redirect
            return '/static/course/course-default-icon.png'


class CourseClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    ranking_size = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return self.course.code + ' – ' + self.code

    class Meta:
        verbose_name_plural = "Classes"
        db_table = 'course_class'
        unique_together = ('code', 'course')


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True)
    id_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.full_name
        # return "%s (%s)" % (self.full_name, self.id_number)

    def enrollments(self):
        return ", ".join(str(x.course_class) for x in self.enrollment_set.all())


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s (%s)" % (self.student, self.course_class)

    def total_score(self):
        score = self.grade_set.all().aggregate(
            score = Sum(
                Case(
                    When(is_canceled=True, then=0),
                    When(assignment_task__points=None, then=F('score')),
                    default=F('score') * F('assignment_task__points'),
                    output_field=IntegerField()
                )
            )
        )['score']

        if score == None:
            score = 0

        return score

    class Meta:
        unique_together = ('student', 'course_class')
        

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.full_name
        

class ClassInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s (%s)" % (self.instructor, self.course_class)
        
    class Meta:
        unique_together = ('instructor', 'course_class')


class Task(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=2000, blank=True)
    enabled_from = models.DateField(null=True, blank=True)
    enabled_until = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000, blank=True)
    enabled_from = models.DateField(null=True, blank=True)
    enabled_until = models.DateField(null=True, blank=True)
    is_optional = models.BooleanField(default=False)
    tasks = models.ManyToManyField(Task, through='AssignmentTask')

    def __str__(self):
        return self.name

    def points (self):
        return self.assignmenttask_set.all().filter(
            is_optional=False
        ).aggregate(
            total = Sum('points')
        )['total']

    def ordered_assignment_tasks(self):
        return self.assignmenttask_set.order_by('is_optional', 'id').all()


class AssignmentTask(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    points = models.IntegerField(null=True, blank=True)
    enrollments = models.ManyToManyField(Enrollment, through='Grade')
    is_optional = models.BooleanField(default=False)

    def __str__(self):
        return "%s – %s" % (self.assignment, self.task)

    class Meta:
        verbose_name = "Assignment Task"
        verbose_name_plural = "Assignment Tasks"
        db_table = 'course_assignment_task'
        unique_together = ('assignment', 'task')


class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    assignment_task = models.ForeignKey(AssignmentTask, on_delete=models.CASCADE)
    score = models.FloatField()
    is_canceled = models.BooleanField(default=False, verbose_name='Canceled')

    class Meta:
        unique_together = ('enrollment', 'assignment_task')

    @property
    def points(self):
        if self.score == None:
            return None
        elif self.assignment_task.points == None:
            return round(self.score)
        else:
            return round(self.score * self.assignment_task.points)
    
    def __str__(self):
        if self.points != None and self.assignment_task_id != None and self.enrollment != None:
            return "%d XP : %s, by %s" % (self.points, self.assignment_task, self.enrollment)
        else:
            return "Grade"

    def clean(self):
        super(Grade, self).clean()

        if self.score != None:
            if self.assignment_task.points == None and not self.score.is_integer():
                raise ValidationError(
                    {
                        'score': _('Score must be an integer value, since the assignment task has no points')
                    },
                    code='invalid'
                )
            elif self.assignment_task.points != None and (self.score < 0 or self.score > 1):
                raise ValidationError(
                    {
                        'score': _('Score must be a value between 0 and 1, representing the percentage of the assignment task points')
                    },
                    code='invalid'
                )
        
        
class Post(models.Model):
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    markdown_text = models.TextField()
    html_code = models.TextField(blank=True)
    post_datetime = models.DateTimeField(auto_now_add=True, blank=True)
    is_pinned_to_the_top = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    