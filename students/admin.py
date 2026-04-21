from django.contrib import admin
from .models import Student, Course, Trainer, Attendance

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Trainer)
admin.site.register(Attendance)