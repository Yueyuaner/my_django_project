from django.contrib import admin

from django.contrib import admin
from .models import SalaryItemType, SalaryItem, SalaryStructure, SalaryStructureDetail, EmployeeSalaryConfig, EmployeeSalaryItem, SalaryPayment, SalaryPaymentDetail
from personnel.models import Employee

# 薪资结构详情内联显示
class SalaryStructureDetailInline(admin.TabularInline):
    model = SalaryStructureDetail
    extra = 2
    fields = ('salary_item', 'amount', 'sort_order', 'formula', 'is_fixed')

# 员工薪资项内联显示
class EmployeeSalaryItemInline(admin.TabularInline):
    model = EmployeeSalaryItem
    extra = 2
    fields = ('salary_item', 'amount', 'is_fixed', 'effective_date')

# 薪资发放详情内联显示
class SalaryPaymentDetailInline(admin.TabularInline):
    model = SalaryPaymentDetail
    extra = 3
    fields = ('salary_item', 'amount', 'note')

# 薪资项类型管理类
class SalaryItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_taxable', 'is_benefit', 'is_deduction')
    list_filter = ('is_taxable', 'is_benefit', 'is_deduction')
    search_fields = ('name', 'code')
    ordering = ('code',)
    fields = ('name', 'code', 'is_taxable', 'is_benefit', 'is_deduction', 'description')

# 薪资项管理类
class SalaryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'item_type', 'default_amount', 'is_active')
    list_filter = ('item_type', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('code',)
    fields = ('name', 'code', 'item_type', 'default_amount', 'is_active', 'description')

# 薪资结构管理类
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'create_time')
    list_filter = ('is_default',)
    search_fields = ('name',)
    ordering = ('-create_time',)
    fields = ('name', 'description', 'is_default')
    inlines = [SalaryStructureDetailInline]

# 员工薪资配置管理类
class EmployeeSalaryConfigAdmin(admin.ModelAdmin):
    list_display = ('employee', 'basic_salary', 'position_salary', 'performance_salary', 'effective_date')
    search_fields = ('employee__name', 'employee__employee_id')
    ordering = ('-effective_date',)
    fieldsets = (
        ('基本信息', {
            'fields': ('employee', 'salary_structure', 'effective_date')
        }),
        ('薪资构成', {
            'fields': ('basic_salary', 'position_salary', 'performance_salary', 'bonus')
        }),
        ('保险基数', {
            'fields': ('social_insurance_base', 'medical_insurance_base', 'housing_fund_base', 'tax_exemption')
        }),
        ('其他信息', {
            'fields': ('note',)
        })
    )
    inlines = [EmployeeSalaryItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'salary_structure')

# 薪资发放记录管理类
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payment_month', 'payment_date', 'basic_salary', 'gross_salary', 'net_salary', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'payment_month')
    search_fields = ('employee__name', 'employee__employee_id')
    ordering = ('-payment_month',)
    date_hierarchy = 'payment_month'
    fieldsets = (
        ('基本信息', {
            'fields': ('employee', 'payment_month', 'payment_date', 'bank_name', 'bank_account')
        }),
        ('薪资构成', {
            'fields': ('basic_salary', 'position_salary', 'performance_salary', 'bonus',
                      'allowance_total', 'other_income_total', 'gross_salary')
        }),
        ('扣除项', {
            'fields': ('social_insurance_deduction', 'medical_insurance_deduction',
                      'housing_fund_deduction', 'tax_deduction', 'other_deduction_total',
                      'net_salary')
        }),
        ('状态信息', {
            'fields': ('status', 'calculator', 'confirm_time', 'payment_status', 'note')
        })
    )
    inlines = [SalaryPaymentDetailInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'calculator')

# 注册模型
admin.site.register(SalaryItemType, SalaryItemTypeAdmin)
admin.site.register(SalaryItem, SalaryItemAdmin)
admin.site.register(SalaryStructure, SalaryStructureAdmin)
admin.site.register(EmployeeSalaryConfig, EmployeeSalaryConfigAdmin)
admin.site.register(SalaryPayment, SalaryPaymentAdmin)
