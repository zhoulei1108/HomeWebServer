"""
家庭管理上下文处理器
为所有模板提供当前家庭和用户家庭列表信息
"""

def family_context(request):
    """
    为模板添加家庭相关的上下文变量
    """
    context = {}
    
    if request.user.is_authenticated:
        from .models import Family, get_current_family
        
        # 获取用户的所有家庭
        user_families = Family.objects.filter(
            members__user=request.user,
            members__is_active=True
        ).distinct()
        
        # 获取当前家庭
        current_family = get_current_family(request.user)
        
        context.update({
            'user_families': user_families,
            'current_family': current_family,
            'has_multiple_families': user_families.count() > 1,
        })
    
    return context