#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业人力资源管理系统测试数据生成脚本
可以直接在项目根目录下运行，为各个模块生成测试数据

在Windows环境下的运行方法：
1. 确保已安装Python和Django
2. 打开命令提示符，进入项目根目录
3. 执行命令：python generate_test_data.py

脚本功能：
- 创建系统管理员用户和员工权限组
- 生成人事管理数据（部门、职位、员工）
- 生成考勤管理数据（考勤记录、请假申请、加班申请）
- 生成薪资管理数据（薪资项、薪资结构、员工薪资配置）
- 生成绩效管理数据（考核类型、指标、绩效记录）
- 生成招聘管理数据（招聘渠道、需求、应聘者）
"""

import os
import sys
import random
import django
# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_management.settings')
django.setup()

from datetime import datetime, timedelta, time
from django.contrib.auth.models import User, Group



# 导入各个模块的模型
from personnel.models import Department, Position, Employee
from attendance.models import AttendanceRecord, LeaveType, LeaveRequest, OvertimeType, OvertimeRequest
from salary.models import SalaryItemType, SalaryItem, SalaryStructure, EmployeeSalaryConfig, SalaryPayment
from performance.models import PerformanceAppraisalType, PerformanceIndicator, PerformanceTemplate, AppraisalPlan
from recruitment.models import RecruitmentChannel, RecruitmentRequirement, Candidate, Interview

print("开始生成测试数据...")

# 1. 创建系统用户和权限组
print("正在创建系统用户和权限组...")

try:
    # 创建管理员用户
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@company.com',
        password='admin123'
    )
    print(f"  ✅ 创建管理员用户: {admin_user.username}")

except Exception as e:
    print(f"  ⚠️  管理员用户已存在或创建失败: {e}")

try:
    # 创建员工组
    employee_group, created = Group.objects.get_or_create(name='员工')
    if created:
        print(f"  ✅ 创建员工组")
    else:
        print(f"  ✅ 员工组已存在")

except Exception as e:
    print(f"  ⚠️  创建员工组失败: {e}")

# 2. 生成人事管理测试数据
print("\n正在生成人事管理测试数据...")

departments = [
    {"name": "技术部"},
    {"name": "人力资源部"},
    {"name": "财务部"},
    {"name": "市场部"},
    {"name": "行政部"}
]

department_objects = []
for dept in departments:
    try:
        department, created = Department.objects.get_or_create(**dept)
        department_objects.append(department)
        if created:
            print(f"  ✅ 创建部门: {department.name}")
        else:
            print(f"  ✅ 部门已存在: {department.name}")
    except Exception as e:
        print(f"  ⚠️  创建部门失败 {dept['name']}: {e}")

positions = [
    {"name": "经理", "level": 5},
    {"name": "主管", "level": 4},
    {"name": "专员", "level": 3},
    {"name": "助理", "level": 2},
    {"name": "实习生", "level": 1}
]

position_objects = []
for pos in positions:
    try:
        position, created = Position.objects.get_or_create(**pos)
        position_objects.append(position)
        if created:
            print(f"  ✅ 创建职位: {position.name}")
        else:
            print(f"  ✅ 职位已存在: {position.name}")
    except Exception as e:
        print(f"  ⚠️  创建职位失败 {pos['name']}: {e}")

# 生成员工数据
employee_names = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑一", "王二", "陈三", "李想", "刘思", "张梦", "王晨", "李阳"
]

employee_count = 0
for name in employee_names:
    try:
        # 检查员工是否已存在
        if Employee.objects.filter(name=name).exists():
            print(f"  ✅ 员工已存在: {name}")
            continue
            
        # 生成随机的员工信息
        department = random.choice(department_objects)
        position = random.choice(position_objects)
        employee_id = f"EMP{random.randint(1000, 9999)}"
        # 直接选择布尔值，True表示男，False表示女
        gender = random.choice([True, False])
        email = f"{name.lower().replace(' ', '')}@company.com"
        phone = f"138{random.randint(10000000, 99999999)}"
        hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
        # 生成出生日期（18-40岁）
        birthday = datetime.now() - timedelta(days=random.randint(6570, 15000))
        # 生成身份证号（唯一）
        id_card = f"310{random.randint(100000000000, 999999999999)}"
        # 生成地址
        address = f"上海市浦东新区张江高科技园区{random.randint(100, 999)}号"
        
        # 先创建员工相关的用户账号
        username = f"{name}{random.randint(10, 99)}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password='123456'
        )
        user.groups.add(employee_group)
        
        # 然后创建员工（包含所有必要字段）
        employee = Employee.objects.create(
            user=user,
            employee_id=employee_id,
            name=name,
            department=department,
            position=position,
            gender=gender,
            email=email,
            phone=phone,
            birthday=birthday,
            id_card=id_card,
            address=address,
            entry_date=hire_date,
            job_status='regular'
        )
        
        # 最后创建员工档案（只包含EmployeeProfile模型中实际存在的字段）
        from personnel.models import EmployeeProfile
        EmployeeProfile.objects.create(
            employee=employee,
            education_background=random.choice(['high_school', 'college', 'bachelor', 'master', 'doctor']),
            political_status=random.choice(['communist', 'league_member', 'democrat', 'mass'])
        )
        
        employee_count += 1
        print(f"  ✅ 创建员工: {name} ({department.name} - {position.name})")
        
    except Exception as e:
            print(f"  ⚠️  创建员工失败 {name}: {e}")

print(f"  ✅ 共创建/存在 {Employee.objects.count()} 名员工")

# 3. 生成考勤管理测试数据
print("\n正在生成考勤管理测试数据...")

# 请假类型
try:
    leave_types = [
        {"name": "年假"},
        {"name": "病假"},
        {"name": "事假"},
        {"name": "婚假"},
        {"name": "产假"},
        {"name": "陪产假"},
        {"name": "工伤假"}
    ]
    
    for lt in leave_types:
        leave_type, created = LeaveType.objects.get_or_create(**lt)
        if created:
            print(f"  ✅ 创建请假类型: {leave_type.name}")
        else:
            print(f"  ✅ 请假类型已存在: {leave_type.name}")

except Exception as e:
    print(f"  ⚠️  创建请假类型失败: {e}")

# 加班类型
try:
    overtime_types = [
        {"name": "工作日加班"},
        {"name": "周末加班"},
        {"name": "节假日加班"}
    ]
    
    for ot in overtime_types:
        overtime_type, created = OvertimeType.objects.get_or_create(**ot)
        if created:
            print(f"  ✅ 创建加班类型: {overtime_type.name}")
        else:
            print(f"  ✅ 加班类型已存在: {overtime_type.name}")

except Exception as e:
    print(f"  ⚠️  创建加班类型失败: {e}")

# 生成考勤记录
if Employee.objects.exists():
    try:
        employees = list(Employee.objects.all())
        records_count = 0
        
        # 为每位员工生成过去30天的考勤记录
        for employee in employees:
            for i in range(30):
                record_date = datetime.now() - timedelta(days=i)
                
                # 随机决定是否上班（工作日大概率上班，周末大概率不上班）
                is_workday = record_date.weekday() < 5
                should_work = is_workday or random.random() < 0.2  # 周末有20%概率上班
                
                if should_work:
                    # 随机生成考勤状态
                    status_options = ['正常', '迟到', '早退', '缺卡']
                    status_weights = [0.7, 0.15, 0.1, 0.05]
                    status = random.choices(status_options, weights=status_weights, k=1)[0]
                    
                    # 生成签到和签退时间
                    if status != '缺卡':
                        # 正常签到时间范围：8:00-9:30
                        sign_in_hour = 8 + random.randint(0, 90) // 60
                        sign_in_minute = random.randint(0, 90) % 60
                        sign_in_time = record_date.replace(hour=sign_in_hour, minute=sign_in_minute, second=0, microsecond=0)
                        
                        # 正常签退时间范围：17:00-19:00
                        sign_out_hour = 17 + random.randint(0, 120) // 60
                        sign_out_minute = random.randint(0, 120) % 60
                        sign_out_time = record_date.replace(hour=sign_out_hour, minute=sign_out_minute, second=0, microsecond=0)
                        
                        # 如果迟到，签到时间会晚于9:00
                        if status == '迟到':
                            sign_in_hour = 9 + random.randint(0, 60) // 60
                            sign_in_minute = random.randint(0, 60) % 60
                            sign_in_time = record_date.replace(hour=sign_in_hour, minute=sign_in_minute, second=0, microsecond=0)
                        
                        # 如果早退，签退时间会早于18:00
                        if status == '早退':
                            sign_out_hour = 16 + random.randint(0, 60) // 60
                            sign_out_minute = random.randint(0, 60) % 60
                            sign_out_time = record_date.replace(hour=sign_out_hour, minute=sign_out_minute, second=0, microsecond=0)
                        
                        # 转换状态为英文值
                        status_map = {
                            '正常': 'normal',
                            '迟到': 'late',
                            '早退': 'early_leave',
                            '缺卡': 'absent'
                        }
                        status_en = status_map.get(status, 'normal')
                        
                        # 创建考勤记录
                        AttendanceRecord.objects.get_or_create(
                            employee=employee,
                            work_date=record_date.date(),
                            defaults={
                                'check_in_time': sign_in_time,
                                'check_out_time': sign_out_time,
                                'status': status_en,
                                'hours_worked': ((sign_out_time - sign_in_time).seconds / 3600)
                            }
                        )
                        records_count += 1
                    
        print(f"  ✅ 生成了 {records_count} 条考勤记录")
    except Exception as e:
        print(f"  ⚠️  生成考勤记录失败: {e}")

# 生成请假申请
if Employee.objects.exists() and LeaveType.objects.exists():
    try:
        employees = list(Employee.objects.all())
        leave_types = list(LeaveType.objects.all())
        leave_requests_count = 0
        
        # 为部分员工生成请假申请
        for _ in range(10):
            employee = random.choice(employees)
            leave_type = random.choice(leave_types)
            start_date = datetime.now() - timedelta(days=random.randint(1, 60))
            days = random.randint(1, 5)
            end_date = start_date + timedelta(days=days-1)
            
            # 随机决定状态（英文值）
            status = random.choice(['pending', 'approved', 'rejected'])
            
            # 创建请假申请
            leave_request, created = LeaveRequest.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date.date(),
                end_date=end_date.date(),
                defaults={
                    'reason': f"因{leave_type.name}请假",
                    'status': status,
                    'days': days
                }
            )
            
            if created:
                leave_requests_count += 1
        
        print(f"  ✅ 生成了 {leave_requests_count} 条请假申请")
    except Exception as e:
        print(f"  ⚠️  生成请假申请失败: {e}")

# 生成加班申请
if Employee.objects.exists() and OvertimeType.objects.exists():
    try:
        employees = list(Employee.objects.all())
        overtime_types = list(OvertimeType.objects.all())
        overtime_requests_count = 0
        
        # 为部分员工生成加班申请
        for _ in range(15):
            employee = random.choice(employees)
            overtime_type = random.choice(overtime_types)
            overtime_date = datetime.now() - timedelta(days=random.randint(1, 60))
            hours = random.randint(1, 4)
            
            # 随机决定状态（英文值）
            status = random.choice(['pending', 'approved', 'rejected'])
            
            # 生成加班起止时间（time类型）
            start_hour = random.randint(18, 20)  # 18:00-20:00开始加班
            start_minute = random.randint(0, 59)
            start_time = time(start_hour, start_minute, 0)
            
            # 计算结束时间
            end_datetime = datetime.combine(overtime_date.date(), start_time) + timedelta(hours=hours)
            end_time = end_datetime.time()
            
            # 创建加班申请
            overtime_request, created = OvertimeRequest.objects.get_or_create(
                employee=employee,
                overtime_type=overtime_type,
                work_date=overtime_date.date(),
                defaults={
                    'reason': "项目进度紧张，需要加班完成任务",
                    'start_time': start_time,
                    'end_time': end_time,
                    'hours': hours,
                    'status': status
                }
            )
            
            if created:
                overtime_requests_count += 1
        
        print(f"  ✅ 生成了 {overtime_requests_count} 条加班申请")
    except Exception as e:
        print(f"  ⚠️  生成加班申请失败: {e}")

# 4. 生成薪资管理测试数据
print("\n正在生成薪资管理测试数据...")

# 薪资项类型
try:
    salary_item_types = [
        {"name": "收入", "is_taxable": True},
        {"name": "扣除", "is_taxable": False},
        {"name": "福利", "is_taxable": False}
    ]
    
    for sit in salary_item_types:
        # 检查是否已存在对应code的薪资项类型
        if sit["name"] == "收入":
            sit["code"] = "INCOME"
        elif sit["name"] == "扣除":
            sit["code"] = "DEDUCTION"
        elif sit["name"] == "福利":
            sit["code"] = "BENEFIT"
            
        salary_item_type, created = SalaryItemType.objects.get_or_create(**sit)
        if created:
            print(f"  ✅ 创建薪资项类型: {salary_item_type.name}")
        else:
            print(f"  ✅ 薪资项类型已存在: {salary_item_type.name}")

except Exception as e:
    print(f"  ⚠️  创建薪资项类型失败: {e}")

# 薪资项
try:
    income_type = SalaryItemType.objects.get(code='INCOME')
    deduction_type = SalaryItemType.objects.get(code='DEDUCTION')
    benefit_type = SalaryItemType.objects.get(code='BENEFIT')
    
    salary_items = [
        {"name": "基本工资", "code": "BASE_SALARY", "item_type": income_type, "default_amount": 8000},
        {"name": "绩效工资", "code": "PERFORMANCE_SALARY", "item_type": income_type, "default_amount": 3000},
        {"name": "交通补贴", "code": "TRANSPORT_ALLOWANCE", "item_type": income_type, "default_amount": 500},
        {"name": "餐饮补贴", "code": "MEAL_ALLOWANCE", "item_type": income_type, "default_amount": 800},
        {"name": "住房补贴", "code": "HOUSING_ALLOWANCE", "item_type": income_type, "default_amount": 1200},
        {"name": "社保扣除", "code": "SOCIAL_SECURITY", "item_type": deduction_type, "default_amount": 1200},
        {"name": "公积金扣除", "code": "HOUSING_FUND", "item_type": deduction_type, "default_amount": 960},
        {"name": "个人所得税", "code": "INCOME_TAX", "item_type": deduction_type, "default_amount": 500},
        {"name": "节日福利", "code": "FESTIVAL_BENEFIT", "item_type": benefit_type, "default_amount": 200}
    ]
    
    for si in salary_items:
        salary_item, created = SalaryItem.objects.get_or_create(**si)
        if created:
            print(f"  ✅ 创建薪资项: {salary_item.name}")
        else:
            print(f"  ✅ 薪资项已存在: {salary_item.name}")

except Exception as e:
    print(f"  ⚠️  创建薪资项失败: {e}")

# 创建薪资结构
try:
    salary_items = list(SalaryItem.objects.all())
    
    salary_structure, created = SalaryStructure.objects.get_or_create(
        name="标准薪资结构",
        defaults={"description": "公司标准薪资结构"}
    )
    
    if created:
        # 添加薪资项到结构中
        from salary.models import SalaryStructureDetail
        for item in salary_items:
            SalaryStructureDetail.objects.create(
                salary_structure=salary_structure,
                salary_item=item,
                sort_order=salary_items.index(item)
            )
        print(f"  ✅ 创建薪资结构: {salary_structure.name}")

except Exception as e:
    print(f"  ⚠️  创建薪资结构失败: {e}")

# 为员工配置薪资
if Employee.objects.exists() and SalaryStructure.objects.exists():
    try:
        employees = list(Employee.objects.all())
        salary_structure = SalaryStructure.objects.first()
        
        for employee in employees:
            # 根据职位级别调整基本工资
            level_factors = {5: 2.5, 4: 2.0, 3: 1.5, 2: 1.2, 1: 1.0}
            base_factor = level_factors.get(employee.position.level, 1.0)
            base_salary = 8000 * base_factor
            
            # 创建员工薪资配置
            emp_salary_config, created = EmployeeSalaryConfig.objects.get_or_create(
                employee=employee,
                salary_structure=salary_structure,
                defaults={
                    'effective_date': datetime.now() - timedelta(days=random.randint(30, 180)),
                    'basic_salary': base_salary
                }
            )
            
            if created:
                # 添加员工薪资项
                from salary.models import EmployeeSalaryItem
                salary_items = list(SalaryItem.objects.all())
                for item in salary_items:
                    # 根据基本工资计算其他薪资项
                    if item.name == '基本工资':
                        amount = base_salary
                    elif item.name == '绩效工资':
                        amount = base_salary * 0.3 * random.uniform(0.8, 1.2)  # 绩效工资在30%基本工资上下浮动
                    elif item.name == '交通补贴':
                        amount = 500
                    elif item.name == '餐饮补贴':
                        amount = 800
                    elif item.name == '住房补贴':
                        amount = 1200
                    elif item.name == '社保扣除':
                        amount = base_salary * 0.15  # 社保大约为工资的15%
                    elif item.name == '公积金扣除':
                        amount = base_salary * 0.12  # 公积金大约为工资的12%
                    elif item.name == '个人所得税':
                        # 简化的个税计算
                        taxable_income = base_salary - 5000 - base_salary * 0.27  # 起征点5000 + 社保公积金
                        if taxable_income > 0:
                            amount = taxable_income * 0.1  # 简化为10%
                        else:
                            amount = 0
                    else:
                        # 使用default_amount属性而非default_value
                        amount = getattr(item, 'default_amount', 0)
                    
                    EmployeeSalaryItem.objects.create(
                        employee_salary=emp_salary_config,
                        salary_item=item,
                        amount=amount
                    )
                
        print(f"  ✅ 为 {employees.__len__()} 名员工配置了薪资")
    except Exception as e:
        print(f"  ⚠️  为员工配置薪资失败: {e}")

# 5. 生成绩效管理测试数据
print("\n正在生成绩效管理测试数据...")

# 考核类型
try:
    appraisal_types = [
        {"name": "月度考核", "frequency": "月度"},
        {"name": "季度考核", "frequency": "季度"},
        {"name": "年度考核", "frequency": "年度"}
    ]
    
    for at in appraisal_types:
        appraisal_type, created = PerformanceAppraisalType.objects.get_or_create(**at)
        if created:
            print(f"  ✅ 创建考核类型: {appraisal_type.name}")
        else:
            print(f"  ✅ 考核类型已存在: {appraisal_type.name}")

except Exception as e:
    print(f"  ⚠️  创建考核类型失败: {e}")

# 考核指标
try:
    indicators = [
        {"name": "工作效率", "indicator_type": "定量"},
        {"name": "工作质量", "indicator_type": "定性"},
        {"name": "团队协作", "indicator_type": "定性"},
        {"name": "创新能力", "indicator_type": "定性"},
        {"name": "任务完成率", "indicator_type": "定量"}
    ]
    
    for ind in indicators:
        indicator, created = PerformanceIndicator.objects.get_or_create(**ind)
        if created:
            print(f"  ✅ 创建考核指标: {indicator.name}")
        else:
            print(f"  ✅ 考核指标已存在: {indicator.name}")

except Exception as e:
    print(f"  ⚠️  创建考核指标失败: {e}")

# 生成绩效考核计划
if Employee.objects.exists() and PerformanceIndicator.objects.exists():
    try:
        employees = list(Employee.objects.all())
        indicators = list(PerformanceIndicator.objects.all())
        appraisal_types = list(PerformanceAppraisalType.objects.all())
        
        # 生成部分员工的绩效考核计划
        for _ in range(8):
            employee = random.choice(employees)
            appraisal_type = random.choice(appraisal_types)
            
            # 随机选择一个时间段
            start_date = datetime.now() - timedelta(days=random.randint(60, 180))
            end_date = start_date + timedelta(days=random.randint(28, 90))
            due_date = end_date + timedelta(days=7)
            
            # 随机决定状态（英文值）
            status = random.choice(['draft', 'scheduled', 'in_progress', 'completed'])
            
            # 创建考核计划
            plan, created = AppraisalPlan.objects.get_or_create(
                name=f"{employee.name}的{appraisal_type.name}",
                appraisal_type=appraisal_type,
                department=employee.department,
                start_date=start_date.date(),
                end_date=end_date.date(),
                due_date=due_date.date(),
                created_by=employee,
                defaults={
                    'status': status,
                }
            )
        
        print(f"  ✅ 生成了部分员工的绩效考核计划")
    except Exception as e:
        print(f"  ⚠️  生成绩效考核计划失败: {e}")

# 6. 生成招聘管理测试数据
print("\n正在生成招聘管理测试数据...")

# 招聘渠道
try:
    channels = [
        {"name": "内部推荐"},
        {"name": "招聘网站"},
        {"name": "校园招聘"},
        {"name": "猎头公司"},
        {"name": "社交媒体"}
    ]
    
    for ch in channels:
        channel, created = RecruitmentChannel.objects.get_or_create(**ch)
        if created:
            print(f"  ✅ 创建招聘渠道: {channel.name}")
        else:
            print(f"  ✅ 招聘渠道已存在: {channel.name}")

except Exception as e:
    print(f"  ⚠️  创建招聘渠道失败: {e}")

# 招聘需求
try:
    departments = list(Department.objects.all())
    positions = list(Position.objects.all())
    
    # 生成招聘需求
    for _ in range(5):
        department = random.choice(departments)
        position = random.choice(positions)
        
        # 随机决定状态（英文值）
        status = random.choice(['draft', 'submitted', 'approved', 'closed'])

        requirement, created = RecruitmentRequirement.objects.get_or_create(
            department=department,
            position=position,
            defaults={
                'number_of_recruits': random.randint(1, 3),
                'status': status,
                'job_description': f"负责{department.name}的{position.name}相关工作",
                'qualification_requirements': "相关专业背景，具备一定工作经验"
            }
        )
        
        if created:
            print(f"  ✅ 创建招聘需求: {department.name} - {position.name}")
        else:
            print(f"  ✅ 招聘需求已存在: {department.name} - {position.name}")

except Exception as e:
    print(f"  ⚠️  创建招聘需求失败: {e}")

# 应聘者
if RecruitmentChannel.objects.exists():
    try:
        channels = list(RecruitmentChannel.objects.all())
        
        candidate_names = [
            "林小明", "张晓华", "李思思", "王志强", "陈佳宁", 
            "刘洋", "周梦琪", "吴俊杰", "郑晓燕", "黄宇航"
        ]
        
        for name in candidate_names:
            # 随机生成应聘者信息
            gender = random.choice(['male', 'female'])
            email = f"{name.lower().replace(' ', '')}@example.com"
            phone_number = f"139{random.randint(10000000, 99999999)}"
            channel = random.choice(channels)
            
            # 随机决定状态（英文值）
            status = random.choice(['pending', 'screening', 'interviewing', 'pass', 'reject', 'offer'])
            
            # 创建应聘者
            candidate, created = Candidate.objects.get_or_create(
                name=name,
                defaults={
                    'gender': gender,
                    'email': email,
                    'phone_number': phone_number,
                    'channel': channel,
                    'status': status
                }
            )
            
            if created:
                print(f"  ✅ 创建应聘者: {name}")
            else:
                print(f"  ✅ 应聘者已存在: {name}")
        
    except Exception as e:
        print(f"  ⚠️  创建应聘者失败: {e}")

print("\n测试数据生成完成！")