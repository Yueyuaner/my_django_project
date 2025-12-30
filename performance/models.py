from django.db import models
from django.utils import timezone
from personnel.models import Employee, Department, Position

# 绩效考核类型模型
class PerformanceAppraisalType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='考核类型名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='考核类型编码')
    frequency = models.CharField(max_length=20, choices=(('monthly', '月度'), ('quarterly', '季度'), ('semiannually', '半年'), ('annually', '年度')), verbose_name='考核频率')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效考核类型'
        verbose_name_plural = '绩效考核类型管理'
        ordering = ['code']

    def __str__(self):
        return self.name

# 绩效考核指标模型
class PerformanceIndicator(models.Model):
    name = models.CharField(max_length=100, verbose_name='指标名称')
    code = models.CharField(max_length=20, verbose_name='指标编码')
    description = models.TextField(blank=True, null=True, verbose_name='指标描述')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='权重(%)')
    indicator_type = models.CharField(max_length=20, choices=(('quantitative', '定量'), ('qualitative', '定性')), verbose_name='指标类型')
    measurement_method = models.TextField(blank=True, null=True, verbose_name='测量方法')
    target = models.TextField(blank=True, null=True, verbose_name='目标值')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效考核指标'
        verbose_name_plural = '绩效考核指标管理'
        ordering = ['code']
        unique_together = ('code', 'name')

    def __str__(self):
        return self.name

# 绩效考核模板模型
class PerformanceTemplate(models.Model):
    name = models.CharField(max_length=100, verbose_name='模板名称')
    description = models.TextField(blank=True, null=True, verbose_name='模板描述')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='performance_templates', verbose_name='适用部门')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='performance_templates', verbose_name='适用岗位')
    is_default = models.BooleanField(default=False, verbose_name='是否默认模板')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效考核模板'
        verbose_name_plural = '绩效考核模板管理'
        ordering = ['-create_time']

    def __str__(self):
        return self.name

# 绩效考核模板指标模型
class TemplateIndicator(models.Model):
    template = models.ForeignKey(PerformanceTemplate, on_delete=models.CASCADE, related_name='indicators', verbose_name='考核模板')
    indicator = models.ForeignKey(PerformanceIndicator, on_delete=models.CASCADE, related_name='template_indicators', verbose_name='考核指标')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='权重(%)')
    target = models.TextField(blank=True, null=True, verbose_name='目标值')
    measurement_method = models.TextField(blank=True, null=True, verbose_name='测量方法')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '模板指标'
        verbose_name_plural = '模板指标管理'
        unique_together = ('template', 'indicator')
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.template.name} - {self.indicator.name}'

# 绩效考核计划模型
class AppraisalPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name='计划名称')
    appraisal_type = models.ForeignKey(PerformanceAppraisalType, on_delete=models.CASCADE, related_name='appraisal_plans', verbose_name='考核类型')
    template = models.ForeignKey(PerformanceTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='appraisal_plans', verbose_name='考核模板')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='appraisal_plans', verbose_name='考核部门')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    due_date = models.DateField(verbose_name='截止日期')
    status = models.CharField(max_length=20, choices=(('draft', '草稿'), ('scheduled', '已计划'), ('in_progress', '进行中'), ('completed', '已完成'), ('closed', '已关闭')), default='draft', verbose_name='状态')
    description = models.TextField(blank=True, null=True, verbose_name='计划描述')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appraisal_plans', verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '考核计划'
        verbose_name_plural = '考核计划管理'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.appraisal_type.name} - {self.start_date.strftime("%Y年%m月")} 考核计划'

# 绩效考核记录模型
class AppraisalRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='appraisal_records', verbose_name='员工')
    plan = models.ForeignKey(AppraisalPlan, on_delete=models.CASCADE, related_name='appraisal_records', verbose_name='考核计划')
    appraiser = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='appraised_records', verbose_name='考核人')
    start_date = models.DateField(verbose_name='考核周期开始日期')
    end_date = models.DateField(verbose_name='考核周期结束日期')
    self_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='自评分数')
    appraiser_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='考核人分数')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='最终分数')
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name='等级')
    status = models.CharField(max_length=20, choices=(('draft', '草稿'), ('self_assessment', '自评中'), ('appraisal', '考核中'), ('review', '审核中'), ('completed', '已完成'), ('rejected', '已驳回')), default='draft', verbose_name='状态')
    self_comment = models.TextField(blank=True, null=True, verbose_name='自评意见')
    appraiser_comment = models.TextField(blank=True, null=True, verbose_name='考核人意见')
    review_comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    self_assessment_time = models.DateTimeField(blank=True, null=True, verbose_name='自评完成时间')
    appraisal_time = models.DateTimeField(blank=True, null=True, verbose_name='考核完成时间')
    review_time = models.DateTimeField(blank=True, null=True, verbose_name='审核完成时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '考核记录'
        verbose_name_plural = '考核记录管理'
        ordering = ['-end_date']
        unique_together = ('employee', 'plan')

    def __str__(self):
        return f'{self.employee.name} - {self.plan.name} 考核记录'

# 考核指标评分模型
class IndicatorScore(models.Model):
    appraisal_record = models.ForeignKey(AppraisalRecord, on_delete=models.CASCADE, related_name='indicator_scores', verbose_name='考核记录')
    indicator = models.ForeignKey(PerformanceIndicator, on_delete=models.CASCADE, related_name='indicator_scores', verbose_name='考核指标')
    self_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='自评分数')
    appraiser_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='考核人分数')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='最终分数')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='权重(%)')
    self_comment = models.TextField(blank=True, null=True, verbose_name='自评说明')
    appraiser_comment = models.TextField(blank=True, null=True, verbose_name='考核人说明')

    class Meta:
        verbose_name = '指标评分'
        verbose_name_plural = '指标评分管理'
        unique_together = ('appraisal_record', 'indicator')

    def __str__(self):
        return f'{self.appraisal_record.employee.name} - {self.indicator.name} 评分'

# 绩效等级模型
class PerformanceGrade(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='等级名称')
    code = models.CharField(max_length=10, unique=True, verbose_name='等级编码')
    min_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='最低分数')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='最高分数')
    description = models.TextField(blank=True, null=True, verbose_name='等级描述')
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name='代表颜色')

    class Meta:
        verbose_name = '绩效等级'
        verbose_name_plural = '绩效等级管理'
        ordering = ['min_score']

    def __str__(self):
        return self.name

# 绩效反馈模型
class PerformanceFeedback(models.Model):
    appraisal_record = models.ForeignKey(AppraisalRecord, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='考核记录')
    feedback_provider = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='provided_feedbacks', verbose_name='反馈提供者')
    content = models.TextField(verbose_name='反馈内容')
    improvement_suggestions = models.TextField(blank=True, null=True, verbose_name='改进建议')
    is_private = models.BooleanField(default=False, verbose_name='是否私密')
    feedback_time = models.DateTimeField(auto_now_add=True, verbose_name='反馈时间')

    class Meta:
        verbose_name = '绩效反馈'
        verbose_name_plural = '绩效反馈管理'
        ordering = ['-feedback_time']

    def __str__(self):
        return f'{self.appraisal_record.employee.name} - {self.feedback_provider.name if self.feedback_provider else "系统"} 反馈'

# 绩效申诉模型
class PerformanceAppeal(models.Model):
    appraisal_record = models.OneToOneField(AppraisalRecord, on_delete=models.CASCADE, related_name='appeal', verbose_name='考核记录')
    reason = models.TextField(verbose_name='申诉原因')
    evidence = models.TextField(blank=True, null=True, verbose_name='证据说明')
    status = models.CharField(max_length=20, choices=(('pending', '待处理'), ('reviewing', '审核中'), ('accepted', '已受理'), ('rejected', '已驳回'), ('closed', '已关闭')), default='pending', verbose_name='状态')
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_appeals', verbose_name='审核人')
    review_comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    appeal_time = models.DateTimeField(auto_now_add=True, verbose_name='申诉时间')
    review_time = models.DateTimeField(blank=True, null=True, verbose_name='审核时间')

    class Meta:
        verbose_name = '绩效申诉'
        verbose_name_plural = '绩效申诉管理'
        ordering = ['-appeal_time']

    def __str__(self):
        return f'{self.appraisal_record.employee.name} 绩效申诉'

# 绩效统计模型
class PerformanceStatistics(models.Model):
    period = models.DateField(verbose_name='统计期间')
    period_type = models.CharField(max_length=20, choices=(('month', '月度'), ('quarter', '季度'), ('year', '年度')), default='month', verbose_name='统计周期类型')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='performance_statistics', verbose_name='部门')
    total_employees = models.IntegerField(default=0, verbose_name='考核员工总数')
    average_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='平均分数')
    grade_distribution = models.JSONField(blank=True, null=True, verbose_name='等级分布')
    improvement_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='进步率(%)')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '绩效统计'
        verbose_name_plural = '绩效统计管理'
        ordering = ['-period']
        unique_together = ('period', 'period_type', 'department')

    def __str__(self):
        dept_name = self.department.name if self.department else '全公司'
        return f'{dept_name} - {self.period.strftime("%Y年%m月")} 绩效统计'
