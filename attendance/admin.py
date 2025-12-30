from django.contrib import admin

from django.contrib import admin
from .models import AttendanceRecord, LeaveType, LeaveRequest, OvertimeType, OvertimeRequest, AttendanceSummary
from personnel.models import Employee

# 考勤记录管理类
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'work_date', 'check_in_time', 'check_out_time', 'hours_worked', 'status')
    list_filter = ('work_date', 'status', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id')
    ordering = ('-work_date', 'employee')
    fields = ('employee', 'work_date', 'check_in_time', 'check_out_time', 'status', 'note')
    date_hierarchy = 'work_date'

    # 自定义显示员工名称
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # 预加载员工数据，减少数据库查询
        return queryset.select_related('employee')

# 请假类型管理类
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_paid', 'annual_quota')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'description', 'is_paid', 'annual_quota')

# 请假申请管理类
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'days', 'status', 'approver', 'create_time')
    list_filter = ('status', 'leave_type', 'start_date', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id', 'reason')
    ordering = ('-create_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'start_time', 'end_time', 'days', 'reason')
        }),
        ('审批信息', {
            'fields': ('status', 'approver', 'approval_time', 'note')
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'leave_type', 'approver')

# 加班类型管理类
class OvertimeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'multiplier')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'description', 'multiplier')

# 加班申请管理类
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'overtime_type', 'work_date', 'start_time', 'end_time', 'hours', 'status', 'approver')
    list_filter = ('status', 'overtime_type', 'work_date', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id', 'reason')
    ordering = ('-work_date',)
    fieldsets = (
        ('基本信息', {
            'fields': ('employee', 'overtime_type', 'work_date', 'start_time', 'end_time', 'hours', 'reason')
        }),
        ('审批信息', {
            'fields': ('status', 'approver', 'approval_time', 'note')
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'overtime_type', 'approver')

# 考勤统计管理类
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'year', 'month', 'normal_days', 'late_count', 'early_leave_count', 'absent_days', 'leave_days', 'overtime_hours')
    list_filter = ('year', 'month', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id')
    ordering = ('-year', '-month', 'employee')
    fields = ('employee', 'year', 'month', 'normal_days', 'late_count', 'early_leave_count', 'absent_days', 'leave_days', 'overtime_hours', 'work_from_home_days', 'note')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee')

# 注册模型
admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(OvertimeType, OvertimeTypeAdmin)
admin.site.register(OvertimeRequest, OvertimeRequestAdmin)
admin.site.register(AttendanceSummary, AttendanceSummaryAdmin)
