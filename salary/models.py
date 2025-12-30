from django.db import models
from django.utils import timezone
from personnel.models import Employee
from attendance.models import AttendanceSummary

# 薪资项类型模型
class SalaryItemType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='薪资项类型名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='薪资项类型编码')
    is_taxable = models.BooleanField(default=True, verbose_name='是否应税')
    is_benefit = models.BooleanField(default=False, verbose_name='是否福利')
    is_deduction = models.BooleanField(default=False, verbose_name='是否扣除项')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        verbose_name = '薪资项类型'
        verbose_name_plural = '薪资项类型管理'
        ordering = ['code']

    def __str__(self):
        return self.name

# 薪资项模型
class SalaryItem(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='薪资项名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='薪资项编码')
    item_type = models.ForeignKey(SalaryItemType, on_delete=models.CASCADE, related_name='salary_items', verbose_name='薪资项类型')
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='默认金额')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        verbose_name = '薪资项'
        verbose_name_plural = '薪资项管理'
        ordering = ['code']

    def __str__(self):
        return self.name

# 薪资结构模型
class SalaryStructure(models.Model):
    name = models.CharField(max_length=100, verbose_name='薪资结构名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_default = models.BooleanField(default=False, verbose_name='是否默认结构')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '薪资结构'
        verbose_name_plural = '薪资结构管理'
        ordering = ['-create_time']

    def __str__(self):
        return self.name

# 薪资结构详情模型
class SalaryStructureDetail(models.Model):
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, related_name='details', verbose_name='薪资结构')
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, related_name='structure_details', verbose_name='薪资项')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='金额')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    formula = models.CharField(max_length=200, blank=True, null=True, verbose_name='计算公式')
    is_fixed = models.BooleanField(default=False, verbose_name='是否固定金额')

    class Meta:
        verbose_name = '薪资结构详情'
        verbose_name_plural = '薪资结构详情管理'
        unique_together = ('salary_structure', 'salary_item')
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.salary_structure.name} - {self.salary_item.name}'

# 员工薪资配置模型
class EmployeeSalaryConfig(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_config', verbose_name='员工')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_configs', verbose_name='薪资结构')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基本工资')
    position_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='岗位工资')
    performance_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绩效工资')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='奖金')
    social_insurance_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='社保基数')
    medical_insurance_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='医保基数')
    housing_fund_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='公积金基数')
    tax_exemption = models.DecimalField(max_digits=10, decimal_places=2, default=5000, verbose_name='个税起征点')
    effective_date = models.DateField(default=timezone.now, verbose_name='生效日期')
    note = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '员工薪资配置'
        verbose_name_plural = '员工薪资配置管理'
        ordering = ['-effective_date']

    def __str__(self):
        return f'{self.employee.name} 的薪资配置'

# 员工薪资项详情模型
class EmployeeSalaryItem(models.Model):
    employee_salary = models.ForeignKey(EmployeeSalaryConfig, on_delete=models.CASCADE, related_name='salary_items', verbose_name='员工薪资配置')
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, related_name='employee_items', verbose_name='薪资项')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='金额')
    is_fixed = models.BooleanField(default=False, verbose_name='是否固定')
    effective_date = models.DateField(default=timezone.now, verbose_name='生效日期')

    class Meta:
        verbose_name = '员工薪资项'
        verbose_name_plural = '员工薪资项管理'
        unique_together = ('employee_salary', 'salary_item')

    def __str__(self):
        return f'{self.employee_salary.employee.name} - {self.salary_item.name}'

# 薪资发放记录模型
class SalaryPayment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_payments', verbose_name='员工')
    payment_month = models.DateField(verbose_name='发放月份')
    payment_date = models.DateField(blank=True, null=True, verbose_name='发放日期')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基本工资')
    position_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='岗位工资')
    performance_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绩效工资')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='奖金')
    allowance_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='津贴补贴合计')
    other_income_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='其他收入合计')
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='应发工资')
    social_insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='社保扣除')
    medical_insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='医保扣除')
    housing_fund_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='公积金扣除')
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='个税扣除')
    other_deduction_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='其他扣除合计')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实发工资')
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='银行名称')
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name='银行账号')
    status = models.CharField(max_length=20, choices=(('draft', '草稿'), ('calculated', '已计算'), ('confirmed', '已确认'), ('paid', '已发放'), ('canceled', '已取消')), default='draft', verbose_name='状态')
    calculator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='calculated_salaries', verbose_name='计算人')
    confirm_time = models.DateTimeField(blank=True, null=True, verbose_name='确认时间')
    payment_status = models.BooleanField(default=False, verbose_name='是否已付款')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '薪资发放记录'
        verbose_name_plural = '薪资发放记录管理'
        ordering = ['-payment_month']
        unique_together = ('employee', 'payment_month')

    def __str__(self):
        return f'{self.employee.name} - {self.payment_month.strftime("%Y年%m月")} 薪资'

# 薪资发放详情模型
class SalaryPaymentDetail(models.Model):
    salary_payment = models.ForeignKey(SalaryPayment, on_delete=models.CASCADE, related_name='details', verbose_name='薪资发放记录')
    salary_item = models.ForeignKey(SalaryItem, on_delete=models.CASCADE, related_name='payment_details', verbose_name='薪资项')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='金额')
    note = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '薪资发放详情'
        verbose_name_plural = '薪资发放详情管理'
        unique_together = ('salary_payment', 'salary_item')

    def __str__(self):
        return f'{self.salary_payment.employee.name} - {self.salary_item.name} - {self.amount}'
