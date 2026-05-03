from django.shortcuts import render, redirect
from .models import Student, Attendance, Trainer, Course
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.models import User

def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="12345678"
        )
        return HttpResponse("Admin created")

    return HttpResponse("Admin already exists")
def export_attendance_excel(request):

    attendances = Attendance.objects.select_related("student", "student__course")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance Report"

    # العناوين
    ws.append([
        "اسم الطالب",
        "الدورة",
        "رقم الهوية",
        "رقم الجوال",
        "التاريخ",
        "الحالة"
    ])

    for a in attendances:

        status = ""

        if a.status == "present":
            status = "حاضر"
        elif a.status == "absent":
            status = "غائب"
        elif a.status == "late":
            status = "متأخر"

        ws.append([
            a.student.name,
            a.student.course.name,
            a.student.national_id,
            a.student.phone,
            str(a.date),
            status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="attendance_report.xlsx"'

    wb.save(response)

    return response

@login_required
def trainer_dashboard(request):

    trainer = Trainer.objects.get(user=request.user)

    students = Student.objects.filter(course__trainer=trainer)

    # قراءة التاريخ من الرابط
    date_str = request.GET.get("date")

    if date_str:
        today = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        today = date.today()

    attendance_today = {}

    for student in students:

        record = Attendance.objects.filter(
            student=student,
            date=today
        ).first()

        if record:
            attendance_today[student.id] = record.status
        else:
            attendance_today[student.id] = None

    return render(request, "trainer_dashboard.html", {
        "students": students,
        "attendance_today": attendance_today,
      "today": today.strftime("%Y-%m-%d")  
    })


@login_required
def take_attendance(request):

    if request.method == "POST":

        date_str = request.POST.get("date")

        if date_str:
            attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            attendance_date = date.today()

        for key, value in request.POST.items():

            if key.startswith("status_"):
                student_id = key.split("_")[1]
                student = Student.objects.get(id=student_id)

                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': value}
                )

        return redirect(f'/trainer/?date={attendance_date}')

    return redirect('/trainer/')