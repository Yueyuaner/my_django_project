from django.core.cache import cache
import hashlib
from django_redis import get_redis_connection

def get_candidate_cache_key(params):
    """根据查询参数生成唯一缓存键（处理分页、筛选条件）"""
    # 参数排序后拼接，避免因参数顺序不同导致键重复
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    # 哈希处理长参数，避免键过长
    hash_str = hashlib.md5(param_str.encode()).hexdigest()
    return f"cache:candidate:{hash_str}"

def get_candidate_list_cache(params):
    """获取候选人列表缓存"""
    key = get_candidate_cache_key(params)
    return cache.get(key)

def set_candidate_list_cache(params, data, timeout=60*30):
    """设置候选人列表缓存（默认30分钟过期）"""
    key = get_candidate_cache_key(params)
    cache.set(key, data, timeout)

def delete_candidate_related_cache():
    """删除所有候选人相关缓存（使用SCAN替代KEYS，避免生产环境阻塞）"""
    conn = get_redis_connection()
    cursor = 0
    while True:
        cursor, keys = conn.scan(cursor, match="cache:candidate:*", count=100)
        if keys:
            conn.delete(*keys)
        if cursor == 0:
            break