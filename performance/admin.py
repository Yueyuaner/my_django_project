from django.contrib import admin

from django.contrib import admin
from .models import PerformanceAppraisalType, PerformanceIndicator, PerformanceTemplate, TemplateIndicator, AppraisalPlan, AppraisalRecord, IndicatorScore, PerformanceGrade, PerformanceFeedback, PerformanceAppeal, PerformanceStatistics
from personnel.models import Employee, Department, Position

# 模板指标内联显示
class TemplateIndicatorInline(admin.TabularInline):
    model = TemplateIndicator
    extra = 3
    fields = ('indicator', 'weight', 'target', 'measurement_method', 'sort_order')

# 指标评分内联显示
class IndicatorScoreInline(admin.TabularInline):
    model = IndicatorScore
    extra = 3
    fields = ('indicator', 'self_score', 'appraiser_score', 'final_score', 'weight', 'self_comment', 'appraiser_comment')

# 绩效反馈内联显示
class PerformanceFeedbackInline(admin.TabularInline):
    model = PerformanceFeedback
    extra = 1
    fields = ('feedback_provider', 'content', 'improvement_suggestions', 'is_private')

# 绩效考核类型管理类
class PerformanceAppraisalTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'frequency', 'is_active', 'create_time')
    list_filter = ('frequency', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('code',)
    fields = ('name', 'code', 'frequency', 'description', 'is_active')

# 绩效考核指标管理类
class PerformanceIndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'indicator_type', 'weight', 'is_active')
    list_filter = ('indicator_type', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('code',)
    fields = ('name', 'code', 'description', 'weight', 'indicator_type', 'measurement_method', 'target', 'is_active')

# 绩效考核模板管理类
class PerformanceTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'position', 'is_default', 'is_active', 'create_time')
    list_filter = ('is_default', 'is_active', 'department', 'position')
    search_fields = ('name',)
    ordering = ('-create_time',)
    fields = ('name', 'description', 'department', 'position', 'is_default', 'is_active')
    inlines = [TemplateIndicatorInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('department', 'position')

# 绩效考核计划管理类
class AppraisalPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'appraisal_type', 'template', 'department', 'start_date', 'end_date', 'status', 'created_by')
    list_filter = ('appraisal_type', 'status', 'department')
    search_fields = ('name',)
    ordering = ('-start_date',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'appraisal_type', 'template', 'department')
        }),
        ('时间信息', {
            'fields': ('start_date', 'end_date', 'due_date')
        }),
        ('其他信息', {
            'fields': ('status', 'description', 'created_by')
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('appraisal_type', 'template', 'department', 'created_by')

# 绩效考核记录管理类
class AppraisalRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'plan', 'appraiser', 'start_date', 'end_date', 'self_score', 'appraiser_score', 'final_score', 'grade', 'status')
    list_filter = ('plan', 'status', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id')
    ordering = ('-end_date',)
    fieldsets = (
        ('关联信息', {
            'fields': ('employee', 'plan', 'appraiser')
        }),
        ('时间信息', {
            'fields': ('start_date', 'end_date')
        }),
        ('评分信息', {
            'fields': ('self_score', 'appraiser_score', 'final_score', 'grade')
        }),
        ('状态信息', {
            'fields': ('status', 'self_comment', 'appraiser_comment', 'review_comment', 'self_assessment_time', 'appraisal_time', 'review_time')
        })
    )
    inlines = [IndicatorScoreInline, PerformanceFeedbackInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'plan', 'appraiser')

# 考核指标评分管理类（独立显示，也在考核记录中内联显示）
class IndicatorScoreAdmin(admin.ModelAdmin):
    list_display = ('appraisal_record', 'indicator', 'self_score', 'appraiser_score', 'final_score', 'weight')
    search_fields = ('appraisal_record__employee__name', 'indicator__name')
    fields = ('appraisal_record', 'indicator', 'self_score', 'appraiser_score', 'final_score', 'weight', 'self_comment', 'appraiser_comment')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('appraisal_record', 'indicator')

# 绩效等级管理类
class PerformanceGradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'min_score', 'max_score')
    search_fields = ('name', 'code')
    ordering = ('min_score',)
    fields = ('name', 'code', 'min_score', 'max_score', 'description', 'color')

# 绩效反馈管理类（独立显示，也在考核记录中内联显示）
class PerformanceFeedbackAdmin(admin.ModelAdmin):
    list_display = ('appraisal_record', 'feedback_provider', 'feedback_time', 'is_private')
    list_filter = ('is_private',)
    search_fields = ('appraisal_record__employee__name', 'content')
    ordering = ('-feedback_time',)
    fields = ('appraisal_record', 'feedback_provider', 'content', 'improvement_suggestions', 'is_private')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('appraisal_record', 'feedback_provider')

# 绩效申诉管理类
class PerformanceAppealAdmin(admin.ModelAdmin):
    list_display = ('appraisal_record', 'status', 'reviewer', 'appeal_time', 'review_time')
    list_filter = ('status',)
    search_fields = ('appraisal_record__employee__name', 'reason')
    ordering = ('-appeal_time',)
    fields = ('appraisal_record', 'reason', 'evidence', 'status', 'reviewer', 'review_comment', 'review_time')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('appraisal_record', 'reviewer')

# 绩效统计管理类
class PerformanceStatisticsAdmin(admin.ModelAdmin):
    list_display = ('appraisal_type', 'department', 'average_score', 'grade_distribution_summary')
    list_filter = ('appraisal_type', 'department')
    ordering = ('-statistics_date',)
    fields = ('appraisal_type', 'department', 'statistics_date', 'total_employees', 'completed_employees', 
              'average_score', 'grade_a_count', 'grade_b_count', 'grade_c_count', 'grade_d_count', 'grade_e_count',
              'improvement_suggestions_summary')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('appraisal_type', 'department')

# 注册模型
admin.site.register(PerformanceAppraisalType, PerformanceAppraisalTypeAdmin)
admin.site.register(PerformanceIndicator, PerformanceIndicatorAdmin)
admin.site.register(PerformanceTemplate, PerformanceTemplateAdmin)
admin.site.register(AppraisalPlan, AppraisalPlanAdmin)
admin.site.register(AppraisalRecord, AppraisalRecordAdmin)
admin.site.register(PerformanceGrade, PerformanceGradeAdmin)
admin.site.register(PerformanceAppeal, PerformanceAppealAdmin)
admin.site.register(PerformanceFeedback, PerformanceFeedbackAdmin)
admin.site.register(IndicatorScore, IndicatorScoreAdmin)
