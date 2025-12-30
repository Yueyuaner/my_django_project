from django.shortcuts import render

# Create your views here.

# ======================== 下面是追加的代码 ========================
# 导入缓存工具函数 + 考勤模型
from .cache_utils import get_all_leave_types, get_all_overtime_types
from .models import LeaveRequest, OvertimeType, AttendanceRecord
from django.utils import timezone

# 请假申请页面 - 带Redis缓存（高频访问，必用）
def leave_request_add(request):
    # ✅ 从Redis缓存获取请假类型，不再查数据库
    leave_types = get_all_leave_types()
    context = {
        'leave_types': leave_types,
        'today': timezone.now().date()
    }
    # 表单提交逻辑（预留，你原来有就直接粘贴进来，没有就保留空）
    if request.method == 'POST':
        pass
    return render(request, 'attendance/leave_request_add.html', context)

# 加班申请页面 - 带Redis缓存（高频访问，必用）
def overtime_request_add(request):
    # ✅ 从Redis缓存获取加班类型，不再查数据库
    overtime_types = get_all_overtime_types()
    context = {
        'overtime_types': overtime_types,
        'today': timezone.now().date()
    }
    # 表单提交逻辑（预留，你原来有就直接粘贴进来，没有就保留空）
    if request.method == 'POST':
        pass
    return render(request, 'attendance/overtime_request_add.html', context)

# 考勤记录查询页面（可选新增，也带缓存，按需保留）
def attendance_record_list(request):
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(work_date=today).order_by('-update_time')
    context = {
        'records': records,
        'today': today
    }
    return render(request, 'attendance/attendance_record_list.html', context)