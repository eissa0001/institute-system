from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    duration_months = models.IntegerField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    start_date = models.DateField()
    duration_months = models.IntegerField()
    end_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.duration_months:
            self.end_date = self.start_date + timedelta(days=30 * self.duration_months)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
        ('excused', 'استئذان'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.name} - {self.date}"