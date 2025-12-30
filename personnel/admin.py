from django.contrib import admin

from django.contrib import admin
from .models import Department, Position, Employee, EmployeeProfile, EducationExperience, WorkExperience
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# 员工档案内联显示
class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False
    verbose_name_plural = '员工档案'
    fields = ('education_background', 'major', 'graduate_school', 'graduate_date', 'political_status', 
              'bank_account', 'bank_name', 'social_insurance_number', 'medical_insurance_number', 
              'housing_fund_number', 'note')

# 教育经历内联显示
class EducationExperienceInline(admin.TabularInline):
    model = EducationExperience
    extra = 1
    fields = ('school_name', 'major', 'degree', 'start_date', 'end_date', 'description')

# 工作经历内联显示
class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ('company_name', 'position', 'start_date', 'end_date', 'description')

# 员工管理类
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'gender', 'department', 'position', 'job_status', 'entry_date', 'create_time')
    list_filter = ('department', 'position', 'job_status', 'entry_date')
    search_fields = ('employee_id', 'name', 'phone', 'email', 'id_card')
    ordering = ('-entry_date',)
    inlines = [EmployeeProfileInline, EducationExperienceInline, WorkExperienceInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'employee_id', 'name', 'gender', 'birthday', 'id_card', 'phone', 'email')
        }),
        ('工作信息', {
            'fields': ('department', 'position', 'job_status', 'entry_date', 'leave_date')
        }),
        ('其他信息', {
            'fields': ('address', 'emergency_contact', 'emergency_phone', 'avatar')
        })
    )

# 部门管理类
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'parent_department', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'manager', 'parent_department', 'description', 'is_active')

# 职位管理类
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')
    search_fields = ('name',)
    ordering = ('level', 'name')
    fields = ('name', 'level', 'description')

# 注册模型
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Employee, EmployeeAdmin)
