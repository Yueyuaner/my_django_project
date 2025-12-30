from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

# 导入各模块模型
from .models import Employee, Department, Position
from attendance.models import AttendanceRecord, LeaveRequest, OvertimeType
from performance.models import AppraisalPlan
from recruitment.models import RecruitmentRequirement, Candidate, Interview
from salary.models import EmployeeSalaryConfig
from .cache_utils import get_all_departments, get_all_positions, get_department_employee_count
# 新增AI工具类导入
from utils.ai_utils import generate_data_summary


# 首页视图
def home(request):
    # 获取今日日期
    today = timezone.now().date()
    # 获取本周开始和结束日期
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    # 获取本月开始和结束日期
    start_of_month = today.replace(day=1)
    next_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
    end_of_month = next_month - timedelta(days=1)

    # 人员统计
    employee_stats = {
        'total': Employee.objects.filter(job_status__in=['probation', 'regular']).count(),
        'probation': Employee.objects.filter(job_status='probation').count(),
        'regular': Employee.objects.filter(job_status='regular').count(),
        'departments': len(get_all_departments()),
        'positions': len(get_all_positions()),
        'new_this_month': Employee.objects.filter(entry_date__gte=start_of_month).count(),
        'resigned_this_month': Employee.objects.filter(leave_date__gte=start_of_month).count()
    }

    # 考勤统计
    attendance_stats = {
        'today_attendance': AttendanceRecord.objects.filter(work_date=today).count(),
        'normal_today': AttendanceRecord.objects.filter(work_date=today, status='normal').count(),
        'late_today': AttendanceRecord.objects.filter(work_date=today, status='late').count(),
        'absent_today': AttendanceRecord.objects.filter(work_date=today, status='absent').count(),
        'leave_requests_pending': LeaveRequest.objects.filter(status='pending').count()
    }

    # 最新信息
    latest_info = {
        'latest_employees': Employee.objects.order_by('-entry_date')[:5],
        'latest_attendance': AttendanceRecord.objects.filter(work_date=today).order_by('-update_time')[:5],
        'latest_leave_requests': LeaveRequest.objects.order_by('-create_time')[:5],
        'latest_interviews': Interview.objects.filter(status='scheduled').order_by('interview_time')[:5]
    }

    # 招聘统计
    recruitment_stats = {
        'open_requirements': RecruitmentRequirement.objects.filter(status__in=['submitted', 'approved']).count(),
        'candidates_pending': Candidate.objects.filter(status='pending').count(),
        'interviews_scheduled': Interview.objects.filter(status='scheduled').count()
    }

    # 绩效统计
    performance_stats = {
        'active_appraisal_plans': AppraisalPlan.objects.filter(status='in_progress').count()
    }

    # 薪资统计
    salary_stats = {
        'total_employees_with_salary': EmployeeSalaryConfig.objects.count()
    }

    # 综合统计数据
    stats_data = {
        'employee': employee_stats,
        'attendance': attendance_stats,
        'recruitment': recruitment_stats,
        'performance': performance_stats,
        'salary': salary_stats
    }

    # 部门人员分布（用于图表）
    department_distribution = get_department_employee_count()

    # 本月考勤趋势（用于柱状图）
    attendance_trend = []
    for i in range(1, today.day + 1):
        date = start_of_month.replace(day=i)
        record = AttendanceRecord.objects.filter(work_date=date)
        attendance_trend.append({
            'date': date.strftime('%m-%d'),
            'total': record.count(),
            'normal': record.filter(status='normal').count(),
            'late': record.filter(status='late').count(),
            'absent': record.filter(status='absent').count()
        })

    context = {
        'stats_data': stats_data,
        'latest_info': latest_info,
        'department_distribution': department_distribution,
        'attendance_trend': attendance_trend,
        'today': today,
        'current_time': timezone.now()
    }
    return render(request, 'home/index.html', context)


# 人员统计数据（用于图表和AI分析）
def employee_stats_data(request):
    departments = get_department_employee_count()
    data = list(departments)

    # 新增AI总结逻辑
    need_summary = request.GET.get('summary', 'false').lower() == 'true'
    if need_summary:
        summary = generate_data_summary(data, title="部门人员分布")
        return JsonResponse({
            'data': data,
            'summary': summary
        }, safe=False)

    return JsonResponse(data, safe=False)


# 考勤趋势数据（用于图表）
def attendance_trend_data(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    trend = []
    for i in range(1, today.day + 1):
        date = start_of_month.replace(day=i)
        record = AttendanceRecord.objects.filter(work_date=date)
        trend.append({
            'date': date.strftime('%m-%d'),
            'normal': record.filter(status='normal').count(),
            'late': record.filter(status='late').count(),
            'absent': record.filter(status='absent').count()
        })

    return JsonResponse(trend, safe=False)