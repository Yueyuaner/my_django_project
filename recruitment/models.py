from django.db import models
from django.utils import timezone
from personnel.models import Department, Position, Employee
# 导入缓存删除工具函数
from .utils import delete_candidate_related_cache


# 招聘渠道模型
class RecruitmentChannel(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='渠道名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '招聘渠道'
        verbose_name_plural = '招聘渠道管理'
        ordering = ['name']

    def __str__(self):
        return self.name


# 招聘需求模型
class RecruitmentRequirement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='recruitment_requirements',
                                   verbose_name='需求部门')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='recruitment_requirements',
                                 verbose_name='职位')
    number_of_recruits = models.IntegerField(default=1, verbose_name='招聘人数')
    urgent_level = models.CharField(max_length=20,
                                    choices=(('normal', '普通'), ('urgent', '紧急'), ('very_urgent', '非常紧急')),
                                    default='normal', verbose_name='紧急程度')
    expected_salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                              verbose_name='期望薪资下限')
    expected_salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                              verbose_name='期望薪资上限')
    work_experience_min = models.IntegerField(default=0, verbose_name='最低工作经验(年)')
    work_experience_max = models.IntegerField(blank=True, null=True, verbose_name='最高工作经验(年)')
    education_requirement = models.CharField(max_length=50, blank=True, null=True, verbose_name='学历要求')
    job_description = models.TextField(verbose_name='岗位职责')
    qualification_requirements = models.TextField(verbose_name='任职要求')
    recruiter = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='recruitment_requirements', verbose_name='招聘负责人')
    status = models.CharField(max_length=20, choices=(
    ('draft', '草稿'), ('submitted', '已提交'), ('approved', '已批准'), ('rejected', '已拒绝'), ('closed', '已关闭')),
                              default='draft', verbose_name='状态')
    approval_comment = models.TextField(blank=True, null=True, verbose_name='审批意见')
    approval_time = models.DateTimeField(blank=True, null=True, verbose_name='审批时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '招聘需求'
        verbose_name_plural = '招聘需求管理'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.department.name} - {self.position.name} 招聘需求'


# 应聘者模型（核心修改：添加索引和缓存失效逻辑）
class Candidate(models.Model):
    name = models.CharField(max_length=50, verbose_name='姓名', db_index=True)  # 索引优化
    gender = models.CharField(max_length=10, choices=(('male', '男'), ('female', '女')), verbose_name='性别')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    phone_number = models.CharField(max_length=20, verbose_name='手机号码', db_index=True)  # 索引优化
    email = models.EmailField(blank=True, null=True, verbose_name='电子邮箱', db_index=True)  # 索引优化
    education = models.CharField(max_length=50, blank=True, null=True, verbose_name='学历', db_index=True)  # 索引优化
    work_experience = models.IntegerField(default=0, verbose_name='工作经验(年)', db_index=True)  # 索引优化
    expected_salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                              verbose_name='期望薪资下限')
    expected_salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                              verbose_name='期望薪资上限')
    channel = models.ForeignKey(RecruitmentChannel, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='candidates', verbose_name='招聘渠道')
    recruitment_requirement = models.ForeignKey(RecruitmentRequirement, on_delete=models.SET_NULL, null=True,
                                                blank=True, related_name='candidates', verbose_name='招聘需求')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='简历')
    status = models.CharField(
        max_length=20,
        choices=(('pending', '待处理'), ('screening', '筛选中'), ('interviewing', '面试中'),
                 ('pass', '通过'), ('reject', '拒绝'), ('offer', '已发offer'),
                 ('employed', '已入职'), ('abandoned', '已放弃')),
        default='pending',
        verbose_name='状态',
        db_index=True  # 索引优化（高频筛选字段）
    )
    recruiter = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates',
                                  verbose_name='招聘负责人')
    summary = models.TextField(blank=True, null=True, verbose_name='总结')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)  # 索引优化（排序字段）
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_index=True)  # 索引优化

    class Meta:
        verbose_name = '应聘者'
        verbose_name_plural = '应聘者管理'
        ordering = ['-create_time']

    def __str__(self):
        return self.name

    # 重写保存方法：数据更新时删除缓存
    def save(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().save(*args, **kwargs)

    # 重写删除方法：数据删除时删除缓存
    def delete(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().delete(*args, **kwargs)


# 面试记录模型（新增缓存失效）
class Interview(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews', verbose_name='应聘者')
    interview_type = models.CharField(max_length=50, choices=(
    ('phone', '电话面试'), ('first', '一面'), ('second', '二面'), ('final', '终面')), verbose_name='面试类型')
    interviewers = models.ManyToManyField(Employee, related_name='interviews', verbose_name='面试官')
    interview_time = models.DateTimeField(blank=True, null=True, verbose_name='面试时间')
    interview_location = models.CharField(max_length=100, blank=True, null=True, verbose_name='面试地点')
    status = models.CharField(max_length=20, choices=(
    ('pending', '待安排'), ('scheduled', '已安排'), ('completed', '已完成'), ('canceled', '已取消')), default='pending',
                              verbose_name='状态')
    score = models.IntegerField(blank=True, null=True, verbose_name='面试得分')
    conclusion = models.TextField(blank=True, null=True, verbose_name='面试结论')
    suggestion = models.TextField(blank=True, null=True, verbose_name='建议')
    next_step = models.TextField(blank=True, null=True, verbose_name='下一步安排')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '面试记录'
        verbose_name_plural = '面试记录管理'
        ordering = ['-interview_time']

    def __str__(self):
        return f'{self.candidate.name} - {self.get_interview_type_display()}'

    # 面试记录变更时删除候选人缓存
    def save(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().delete(*args, **kwargs)


# Offer模型（新增缓存失效）
class Offer(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='offer', verbose_name='应聘者')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='offers', verbose_name='部门')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='offers', verbose_name='职位')
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='月薪')
    annual_bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='年终奖')
    benefits = models.TextField(blank=True, null=True, verbose_name='福利待遇')
    start_date = models.DateField(blank=True, null=True, verbose_name='入职日期')
    probation_period = models.IntegerField(default=3, verbose_name='试用期(月)')
    status = models.CharField(max_length=20, choices=(
    ('draft', '草稿'), ('sent', '已发送'), ('accepted', '已接受'), ('rejected', '已拒绝'), ('expired', '已过期')),
                              default='draft', verbose_name='状态')
    sender = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_offers',
                               verbose_name='发送人')
    send_time = models.DateTimeField(blank=True, null=True, verbose_name='发送时间')
    accept_time = models.DateTimeField(blank=True, null=True, verbose_name='接受时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offer管理'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.candidate.name} 的Offer'

    # Offer变更时删除候选人缓存
    def save(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().delete(*args, **kwargs)


# 入职信息模型（新增缓存失效）
class OnboardingInfo(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='onboarding_info',
                                     verbose_name='应聘者')
    employee = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='onboarding_info', verbose_name='员工')
    actual_start_date = models.DateField(blank=True, null=True, verbose_name='实际入职日期')
    id_card_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='身份证号')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='居住地址')
    emergency_contact_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='紧急联系人姓名')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='紧急联系人电话')
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='银行卡所属银行')
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name='银行账号')
    documents_status = models.CharField(max_length=20,
                                        choices=(('pending', '待提交'), ('complete', '已提交'), ('verified', '已审核')),
                                        default='pending', verbose_name='证件材料状态')
    orientation_completed = models.BooleanField(default=False, verbose_name='入职培训完成')
    onboarding_status = models.CharField(max_length=20, choices=(
    ('pending', '待处理'), ('processing', '处理中'), ('completed', '已完成'), ('canceled', '已取消')),
                                         default='pending', verbose_name='入职状态')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '入职信息'
        verbose_name_plural = '入职信息管理'
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.candidate.name} 入职信息'

    # 入职信息变更时删除候选人缓存
    def save(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_candidate_related_cache()
        super().delete(*args, **kwargs)


# 招聘统计模型
class RecruitmentStatistics(models.Model):
    period = models.DateField(verbose_name='统计期间')
    period_type = models.CharField(max_length=20, choices=(('month', '月度'), ('quarter', '季度'), ('year', '年度')),
                                   default='month', verbose_name='统计周期类型')
    total_candidates = models.IntegerField(default=0, verbose_name='应聘者总数')
    interviewed_candidates = models.IntegerField(default=0, verbose_name='面试人数')
    passed_candidates = models.IntegerField(default=0, verbose_name='通过人数')
    offer_candidates = models.IntegerField(default=0, verbose_name='发放Offer人数')
    accepted_offer_candidates = models.IntegerField(default=0, verbose_name='接受Offer人数')
    onboarding_candidates = models.IntegerField(default=0, verbose_name='实际入职人数')
    recruitment_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='招聘成本')
    average_recruitment_time = models.IntegerField(blank=True, null=True, verbose_name='平均招聘周期(天)')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '招聘统计'
        verbose_name_plural = '招聘统计管理'
        ordering = ['-period']
        unique_together = ('period', 'period_type')

    def __str__(self):
        return f'{self.period.strftime("%Y年%m月")} 招聘统计'