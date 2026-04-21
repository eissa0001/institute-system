from django.shortcuts import render, redirect
from .models import Student, Attendance, Trainer, Course
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import openpyxl
from django.http import HttpResponse

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
        "today": today
    })


def take_attendance(request):

    student_id = request.GET.get('student')
    status = request.GET.get('status')
    date_str = request.GET.get("date")

    student = Student.objects.get(id=student_id)

    if date_str:
        attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        attendance_date = date.today()

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=attendance_date,
        defaults={'status': status}
    )

    if not created:
        attendance.status = status
        attendance.save()

    return redirect(f'/trainer/?date={attendance_date}')


@login_required
def attendance_report(request):

    students = Student.objects.all()
    courses = Course.objects.all()
    attendances = Attendance.objects.all()

    course = request.GET.get("course")
    student = request.GET.get("student")
    national_id = request.GET.get("national_id")
    phone = request.GET.get("phone")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if course:
        attendances = attendances.filter(student__course_id=course)

    if student:
        attendances = attendances.filter(student_id=student)

    if national_id:
        attendances = attendances.filter(student__national_id__icontains=national_id)

    if phone:
        attendances = attendances.filter(student__phone__icontains=phone)

    if date_from:
        attendances = attendances.filter(date__gte=date_from)

    if date_to:
        attendances = attendances.filter(date__lte=date_to)

    return render(request, "attendance_report.html", {
        "attendances": attendances,
        "students": students,
        "courses": courses
    })

@login_required
def dashboard(request):

    trainer = Trainer.objects.get(user=request.user)

    return redirect('/trainer/')