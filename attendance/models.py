from django.db import models
from django.utils import timezone
from personnel.models import Employee
from django.core.validators import MinValueValidator, MaxValueValidator

# 考勤记录模型
class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='员工')
    check_in_time = models.DateTimeField(blank=True, null=True, verbose_name='签到时间')
    check_out_time = models.DateTimeField(blank=True, null=True, verbose_name='签退时间')
    work_date = models.DateField(verbose_name='工作日期')
    status = models.CharField(max_length=20, choices=(
        ('normal', '正常'), 
        ('late', '迟到'), 
        ('early_leave', '早退'), 
        ('absent', '缺勤'), 
        ('leave', '请假'),
        ('work_from_home', '居家办公')
    ), default='normal', verbose_name='考勤状态')
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name='工作时长（小时）')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录管理'
        ordering = ['-work_date']
        unique_together = ('employee', 'work_date')

    def __str__(self):
        return f'{self.employee.name} - {self.work_date} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        # 自动计算工作时长
        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            self.hours_worked = round(duration.total_seconds() / 3600, 1)
        super().save(*args, **kwargs)

# 请假类型模型
class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='请假类型名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_paid = models.BooleanField(default=False, verbose_name='是否带薪')
    annual_quota = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='年度额度（天）')

    class Meta:
        verbose_name = '请假类型'
        verbose_name_plural = '请假类型管理'
        ordering = ['name']

    def __str__(self):
        return self.name

# 请假申请模型
class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', verbose_name='员工')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='leave_requests', verbose_name='请假类型')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    start_time = models.TimeField(blank=True, null=True, verbose_name='开始时间')
    end_time = models.TimeField(blank=True, null=True, verbose_name='结束时间')
    days = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='请假天数')
    reason = models.TextField(verbose_name='请假原因')
    status = models.CharField(max_length=20, choices=(
        ('pending', '待审批'), 
        ('approved', '已批准'), 
        ('rejected', '已拒绝'),
        ('canceled', '已取消')
    ), default='pending', verbose_name='状态')
    approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name='审批人')
    approval_time = models.DateTimeField(blank=True, null=True, verbose_name='审批时间')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = '请假申请管理'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.employee.name} - {self.leave_type.name} - {self.start_date} 至 {self.end_date}'

# 加班类型模型
class OvertimeType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='加班类型名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5, verbose_name='倍数')

    class Meta:
        verbose_name = '加班类型'
        verbose_name_plural = '加班类型管理'
        ordering = ['name']

    def __str__(self):
        return self.name

# 加班申请模型
class OvertimeRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_requests', verbose_name='员工')
    overtime_type = models.ForeignKey(OvertimeType, on_delete=models.CASCADE, related_name='overtime_requests', verbose_name='加班类型')
    work_date = models.DateField(verbose_name='加班日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    hours = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='加班时长（小时）')
    reason = models.TextField(verbose_name='加班原因')
    status = models.CharField(max_length=20, choices=(
        ('pending', '待审批'), 
        ('approved', '已批准'), 
        ('rejected', '已拒绝'),
        ('canceled', '已取消')
    ), default='pending', verbose_name='状态')
    approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_overtimes', verbose_name='审批人')
    approval_time = models.DateTimeField(blank=True, null=True, verbose_name='审批时间')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '加班申请'
        verbose_name_plural = '加班申请管理'
        ordering = ['-work_date']

    def __str__(self):
        return f'{self.employee.name} - {self.work_date} - {self.hours}小时'

    def save(self, *args, **kwargs):
        # 自动计算加班时长
        if self.start_time and self.end_time:
            # 处理跨天的情况
            start_datetime = timezone.datetime.combine(self.work_date, self.start_time)
            end_date = self.work_date
            # 如果结束时间小于开始时间，说明跨天
            if self.end_time < self.start_time:
                end_date = end_date + timezone.timedelta(days=1)
            end_datetime = timezone.datetime.combine(end_date, self.end_time)
            duration = end_datetime - start_datetime
            self.hours = round(duration.total_seconds() / 3600, 1)
        super().save(*args, **kwargs)

# 考勤统计模型
class AttendanceSummary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_summaries', verbose_name='员工')
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name='月份')
    normal_days = models.IntegerField(default=0, verbose_name='正常出勤天数')
    late_count = models.IntegerField(default=0, verbose_name='迟到次数')
    early_leave_count = models.IntegerField(default=0, verbose_name='早退次数')
    absent_days = models.IntegerField(default=0, verbose_name='缺勤天数')
    leave_days = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='请假天数')
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='加班小时数')
    work_from_home_days = models.IntegerField(default=0, verbose_name='居家办公天数')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '考勤统计'
        verbose_name_plural = '考勤统计管理'
        ordering = ['-year', '-month']
        unique_together = ('employee', 'year', 'month')

    def __str__(self):
        return f'{self.employee.name} - {self.year}年{self.month}月 考勤统计'
