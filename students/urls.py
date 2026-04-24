from django.urls import path
from .views import take_attendance, trainer_dashboard, attendance_report, dashboard
from django.contrib.auth import views as auth_views
from .views import export_attendance_excel

urlpatterns = [

    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('dashboard/', dashboard, name='dashboard'),

    path('trainer/', trainer_dashboard, name='trainer_dashboard'),

    path('attendance/', take_attendance, name='attendance'),

    path('report/', attendance_report, name='attendance_report'),
    path('report/export/', export_attendance_excel, name='export_excel'),
    

]