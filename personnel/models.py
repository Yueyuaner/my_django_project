from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 部门模型
class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='部门名称')
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments', verbose_name='部门经理')
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_departments', verbose_name='上级部门')
    description = models.TextField(blank=True, null=True, verbose_name='部门描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['name']

    def __str__(self):
        return self.name

# 职位模型
class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name='职位名称')
    level = models.IntegerField(default=1, verbose_name='职位级别')
    description = models.TextField(blank=True, null=True, verbose_name='职位描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位管理'
        ordering = ['level', 'name']

    def __str__(self):
        return self.name

# 员工模型
class Employee(models.Model):
    # 基本信息
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', verbose_name='用户')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='员工工号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.BooleanField(choices=((True, '男'), (False, '女')), verbose_name='性别')
    birthday = models.DateField(verbose_name='出生日期')
    id_card = models.CharField(max_length=18, unique=True, verbose_name='身份证号')
    phone = models.CharField(max_length=11, verbose_name='手机号码')
    email = models.EmailField(verbose_name='邮箱')
    entry_date = models.DateField(verbose_name='入职日期')
    
    # 工作信息
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees', verbose_name='所属部门')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='employees', verbose_name='职位')
    job_status = models.CharField(max_length=20, choices=(('probation', '试用期'), ('regular', '正式'), ('resigned', '已离职')), default='probation', verbose_name='工作状态')
    
    # 其他信息
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='住址')
    emergency_contact = models.CharField(max_length=50, blank=True, null=True, verbose_name='紧急联系人')
    emergency_phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='紧急联系电话')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    
    # 时间信息
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    leave_date = models.DateField(blank=True, null=True, verbose_name='离职日期')

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工管理'
        ordering = ['-entry_date']

    def __str__(self):
        return f'{self.employee_id} - {self.name}'

# 员工档案模型
class EmployeeProfile(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='profile', verbose_name='员工')
    education_background = models.CharField(max_length=50, choices=(('high_school', '高中'), ('college', '专科'), ('bachelor', '本科'), ('master', '硕士'), ('doctor', '博士')), verbose_name='学历')
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业')
    graduate_school = models.CharField(max_length=100, blank=True, null=True, verbose_name='毕业院校')
    graduate_date = models.DateField(blank=True, null=True, verbose_name='毕业日期')
    political_status = models.CharField(max_length=20, choices=(('communist', '中共党员'), ('league_member', '共青团员'), ('democrat', '民主党派'), ('mass', '群众')), default='mass', verbose_name='政治面貌')
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name='银行卡号')
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='银行名称')
    social_insurance_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='社保号')
    medical_insurance_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='医保号')
    housing_fund_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='公积金号')
    note = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '员工档案'
        verbose_name_plural = '员工档案管理'

    def __str__(self):
        return f'{self.employee.name} 的档案'

# 教育经历模型
class EducationExperience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education_experiences', verbose_name='员工')
    school_name = models.CharField(max_length=100, verbose_name='学校名称')
    major = models.CharField(max_length=100, verbose_name='专业')
    degree = models.CharField(max_length=50, choices=(('high_school', '高中'), ('college', '专科'), ('bachelor', '本科'), ('master', '硕士'), ('doctor', '博士')), verbose_name='学历')
    start_date = models.DateField(verbose_name='开始时间')
    end_date = models.DateField(verbose_name='结束时间')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        verbose_name = '教育经历'
        verbose_name_plural = '教育经历管理'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.employee.name} - {self.school_name}'

# 工作经历模型
class WorkExperience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_experiences', verbose_name='员工')
    company_name = models.CharField(max_length=100, verbose_name='公司名称')
    position = models.CharField(max_length=100, verbose_name='职位')
    start_date = models.DateField(verbose_name='开始时间')
    end_date = models.DateField(blank=True, null=True, verbose_name='结束时间')
    description = models.TextField(blank=True, null=True, verbose_name='工作描述')

    class Meta:
        verbose_name = '工作经历'
        verbose_name_plural = '工作经历管理'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.employee.name} - {self.company_name}'
