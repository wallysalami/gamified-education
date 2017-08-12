from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.db.models import Sum

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.code + ' – ' + self.name


class CourseClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    
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
        return "%s -> %s" % (self.student, self.course_class)

    class Meta:
        unique_together = ('student', 'course_class')


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
    tasks = models.ManyToManyField(Task, through='AssignmentTask')

    def __str__(self):
        return self.name

    def points (self):
        return self.assignmenttask_set.all().aggregate(
            total = Sum('points')
        )['total']

    def ordered_assignment_tasks(self):
        return self.assignmenttask_set.order_by('id').all()


class AssignmentTask(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    points = models.IntegerField()
    enrollments = models.ManyToManyField(Enrollment, through='Grade')

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
    percentage = models.FloatField(default=1.0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    def score(self):
        return round(self.percentage * self.assignment_task.points)
    
    def __str__(self):
        return "%d XP : %s, by %s" % (self.score(), self.assignment_task, self.enrollment)

    class Meta:
        unique_together = ('enrollment', 'assignment_task')