"""
测试用户访问权限和家庭数据显示
"""
from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.family.models import get_current_family
from apps.family.views import family_dashboard
from apps.events.models import Event
from apps.housework.models import Housework

def test_user_access():
    factory = RequestFactory()
    
    # 测试test02用户
    test_user = User.objects.get(username='test02')
    print(f"=== 测试用户: {test_user.username} ===")
    
    # 检查当前家庭
    current_family = get_current_family(test_user)
    print(f"当前家庭: {current_family.name if current_family else 'None'}")
    
    # 检查家庭成员状态
    if current_family:
        member = current_family.members.filter(user=test_user, is_active=True).first()
        print(f"成员角色: {member.role if member else 'Not found'}")
        print(f"成员权限: 创建事件={member.can_create_events if member else 'N/A'}, 创建家务={member.can_create_housework if member else 'N/A'}")
        
        # 检查数据访问
        events = Event.objects.filter(family=current_family)
        houseworks = Housework.objects.filter(family=current_family)
        
        print(f"可访问事件数: {events.count()}")
        print(f"可访问家务数: {houseworks.count()}")
        
        # 显示具体数据
        for event in events:
            print(f"  事件: {event.name}")
        for housework in houseworks:
            print(f"  家务: {housework.title}")
    
    print("\n=== 测试结束 ===")

if __name__ == '__main__':
    test_user_access()