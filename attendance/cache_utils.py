from django.core.cache import cache
from .models import LeaveType, OvertimeType

# 缓存所有请假类型
def get_all_leave_types():
    cache_key = "cache:leave_types_all"
    leave_types = cache.get(cache_key)
    if not leave_types:
        leave_types = list(LeaveType.objects.values('id', 'name', 'description'))
        cache.set(cache_key, leave_types, 60*60*24*7)
    return leave_types

# 缓存所有加班类型
def get_all_overtime_types():
    cache_key = "cache:overtime_types_all"
    overtime_types = cache.get(cache_key)
    if not overtime_types:
        overtime_types = list(OvertimeType.objects.values('id', 'name', 'multiplier', 'description'))
        cache.set(cache_key, overtime_types, 60*60*24*7)
    return overtime_types