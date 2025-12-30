from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Candidate
from .utils import get_candidate_list_cache, set_candidate_list_cache

def candidate_list(request):
    """
    应聘者列表查询接口（带缓存逻辑）
    支持筛选条件：status（状态）、page（页码）、page_size（每页条数）
    """
    # 1. 获取查询参数（默认值处理）
    status = request.GET.get('status', '')  # 状态筛选，空表示查询全部
    page = int(request.GET.get('page', 1))  # 页码，默认第1页
    page_size = int(request.GET.get('page_size', 10))  # 每页条数，默认10条

    # 2. 生成缓存参数（包含所有筛选和分页条件，确保缓存键唯一）
    cache_params = {
        'status': status,
        'page': page,
        'page_size': page_size
    }

    # 3. 尝试从缓存获取数据，命中则直接返回
    cached_data = get_candidate_list_cache(cache_params)
    if cached_data:
        return JsonResponse(cached_data)

    # 4. 缓存未命中，执行数据库查询（优化点：预加载关联对象，减少查询次数）
    queryset = Candidate.objects.select_related(
        'recruiter',  # 预加载招聘负责人
        'channel',    # 预加载招聘渠道
        'recruitment_requirement'  # 预加载招聘需求
    )

    # 应用状态筛选
    if status:
        queryset = queryset.filter(status=status)

    # 按创建时间倒序（最新的在前面）
    queryset = queryset.order_by('-create_time')

    # 处理分页
    paginator = Paginator(queryset, page_size)
    total_count = paginator.count  # 总记录数
    total_pages = paginator.num_pages  # 总页数
    current_page = paginator.get_page(page)  # 当前页数据

    # 5. 序列化数据（按需调整返回字段）
    candidate_list = [
        {
            'id': obj.id,
            'name': obj.name,
            'gender': obj.get_gender_display(),  # 显示性别中文
            'phone_number': obj.phone_number,
            'email': obj.email or '',  # 空值处理
            'education': obj.education or '',
            'work_experience': obj.work_experience,
            'status': obj.status,
            'status_display': obj.get_status_display(),  # 显示状态中文
            'recruiter': obj.recruiter.name if obj.recruiter else None,
            'create_time': obj.create_time.strftime('%Y-%m-%d %H:%M:%S')
        } for obj in current_page.object_list
    ]

    # 6. 构建响应数据
    response_data = {
        'total': total_count,
        'total_pages': total_pages,
        'current_page': page,
        'page_size': page_size,
        'results': candidate_list
    }

    # 7. 缓存查询结果（默认30分钟过期）
    set_candidate_list_cache(cache_params, response_data)

    return JsonResponse(response_data)