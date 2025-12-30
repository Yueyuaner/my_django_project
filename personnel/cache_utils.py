# company_management/personnel/cache_utils.py
# 人事模块 Redis缓存工具类 - 完整代码，直接复制粘贴
from django.core.cache import cache
from django.db.models import Count
from .models import Department, Position

# 缓存【所有部门列表】- 首页统计/员工表单下拉框用
def get_all_departments():
    cache_key = "cache:dept_all"
    depts = cache.get(cache_key)
    if not depts:
        depts = list(Department.objects.values('id', 'name', 'description'))
        cache.set(cache_key, depts, 60*60*24*7)  # 缓存7天，部门几乎不变
    return depts

# 缓存【所有职位列表】- 员工表单下拉框用
def get_all_positions():
    cache_key = "cache:position_all"
    positions = cache.get(cache_key)
    if not positions:
        # 去掉不存在的'department__name'，只保留Position实际有的字段（比如id、name、description）
        positions = list(Position.objects.values('id', 'name', 'description'))  # 这里改了！
        cache.set(cache_key, positions, 60*60*24*7)
    return positions

# 缓存【部门人员分布统计】- 首页饼图/图表接口用，重中之重
def get_department_employee_count():
    cache_key = "cache:dept_employee_count"
    dept_count = cache.get(cache_key)
    if not dept_count:
        dept_count = list(Department.objects.annotate(employee_count=Count('employees')).values('name', 'employee_count').order_by('-employee_count'))
        cache.set(cache_key, dept_count, 60*60*24)  # 缓存1天，足够用
    return dept_count