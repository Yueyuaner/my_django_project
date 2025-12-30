from django.urls import path

from . import views

app_name = 'personnel'

urlpatterns = [
    # 首页视图
    path('home/', views.home, name='home'),
    
    # 数据API
    path('api/employee-stats/', views.employee_stats_data, name='employee_stats_data'),
    path('api/attendance-trend/', views.attendance_trend_data, name='attendance_trend_data'),
    path('employee_stats_data/', views.employee_stats_data, name='employee_stats_data'),
]
