from django.contrib import admin
from .models import RecruitmentChannel, RecruitmentRequirement, Candidate, Interview, Offer, OnboardingInfo, RecruitmentStatistics
from personnel.models import Department, Position, Employee

# 面试记录内联显示
class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 1
    fields = ('interview_type', 'interviewers', 'interview_time', 'interview_location', 'status', 'score', 'conclusion')
    filter_horizontal = ('interviewers',)  # 优化多对多字段选择体验

# 招聘渠道管理类
class RecruitmentChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'create_time')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'description', 'is_active')
    save_on_top = True  # 顶部显示保存按钮

# 招聘需求管理类
class RecruitmentRequirementAdmin(admin.ModelAdmin):
    list_display = ('department', 'position', 'number_of_recruits', 'urgent_level', 'status', 'create_time')
    list_filter = ('department', 'position', 'urgent_level', 'status')
    search_fields = ('department__name', 'position__name', 'job_description')
    ordering = ('-create_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('department', 'position', 'number_of_recruits', 'urgent_level', 'recruiter')
        }),
        ('薪资和经验要求', {
            'fields': ('expected_salary_min', 'expected_salary_max', 'work_experience_min', 'work_experience_max', 'education_requirement')
        }),
        ('职位详情', {
            'fields': ('job_description', 'qualification_requirements')
        }),
        ('审批信息', {
            'fields': ('status', 'approval_comment', 'approval_time'),
            'classes': ('collapse',)  # 可折叠区域
        })
    )
    readonly_fields = ('approval_time',)  # 审批时间设为只读
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('department', 'position', 'recruiter')

# 应聘者管理类
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'phone_number', 'email', 'channel', 'status', 'recruiter', 'create_time')
    list_filter = ('gender', 'status', 'channel', 'recruitment_requirement')
    search_fields = ('name', 'phone_number', 'email')
    ordering = ('-create_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'gender', 'birth_date', 'phone_number', 'email')
        }),
        ('求职信息', {
            'fields': ('education', 'work_experience', 'expected_salary_min', 'expected_salary_max')
        }),
        ('招聘相关', {
            'fields': ('channel', 'recruitment_requirement', 'resume', 'status', 'recruiter')
        }),
        ('其他信息', {
            'fields': ('summary', 'create_time'),
            'classes': ('collapse',)
        })
    )
    inlines = [InterviewInline]
    readonly_fields = ('create_time',)  # 创建时间设为只读
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('channel', 'recruitment_requirement', 'recruiter')

# 面试记录管理类（独立显示，也在应聘者中内联显示）
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'interview_type', 'interview_time', 'status', 'score')
    list_filter = ('interview_type', 'status')
    search_fields = ('candidate__name', 'conclusion')
    ordering = ('-interview_time',)
    fields = ('candidate', 'interview_type', 'interviewers', 'interview_time', 'interview_location', 'status', 'score', 'conclusion', 'suggestion', 'next_step')
    filter_horizontal = ('interviewers',)  # 优化多对多字段选择
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('candidate')

# Offer管理类
class OfferAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'department', 'position', 'monthly_salary', 'status', 'create_time')
    list_filter = ('status', 'department', 'position')
    search_fields = ('candidate__name',)
    ordering = ('-create_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('candidate', 'department', 'position')
        }),
        ('薪资福利', {
            'fields': ('monthly_salary', 'annual_bonus', 'benefits')
        }),
        ('入职信息', {
            'fields': ('start_date', 'probation_period')
        }),
        ('状态信息', {
            'fields': ('status', 'sender', 'send_time', 'accept_time'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('send_time', 'accept_time', 'create_time')  # 自动生成的时间设为只读
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('candidate', 'department', 'position', 'sender')

# 入职信息管理类
class OnboardingInfoAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'employee', 'actual_start_date', 'documents_status', 'onboarding_status')
    list_filter = ('documents_status', 'onboarding_status')
    search_fields = ('candidate__name', 'employee__name')
    ordering = ('-create_time',)
    fieldsets = (
        ('关联信息', {
            'fields': ('candidate', 'employee')
        }),
        ('基本信息', {
            'fields': ('actual_start_date', 'id_card_number', 'address')
        }),
        ('紧急联系人', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('银行信息', {
            'fields': ('bank_name', 'bank_account')
        }),
        ('状态信息', {
            'fields': ('documents_status', 'orientation_completed', 'onboarding_status', 'note', 'create_time'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('create_time',)  # 创建时间设为只读
    save_on_top = True

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('candidate', 'employee')

# 招聘统计管理类
class RecruitmentStatisticsAdmin(admin.ModelAdmin):
    list_display = ('period', 'period_type', 'total_candidates', 'interviewed_candidates', 'passed_candidates', 'onboarding_candidates')
    list_filter = ('period_type',)
    ordering = ('-period',)
    fields = ('period', 'period_type', 'total_candidates', 'interviewed_candidates', 'passed_candidates', 'offer_candidates', 'accepted_offer_candidates', 'onboarding_candidates', 'recruitment_cost', 'average_recruitment_time')
    readonly_fields = ('create_time',)  # 假设存在创建时间字段
    save_on_top = True

# 注册模型
admin.site.register(RecruitmentChannel, RecruitmentChannelAdmin)
admin.site.register(RecruitmentRequirement, RecruitmentRequirementAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OnboardingInfo, OnboardingInfoAdmin)
admin.site.register(RecruitmentStatistics, RecruitmentStatisticsAdmin)