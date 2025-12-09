from django.contrib.auth.models import User
from apps.family.models import get_current_family, Family, FamilyMember
from apps.events.models import Event
from apps.housework.models import Housework, HouseworkCategory, create_default_categories
from datetime import datetime, timedelta

# 获取测试用户
user = User.objects.first()
family = get_current_family(user)

if family:
    # 创建默认分类
    create_default_categories()
    
    # 创建测试事件
    event = Event.objects.create(
        name='家庭聚餐',
        family=family,
        creator=user,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=2)
    )
    
    # 创建测试家务
    category = HouseworkCategory.objects.first()
    if category:
        housework = Housework.objects.create(
            title='打扫客厅',
            family=family,
            user=user,
            category=category
        )
    
    print(f'Created test data for family: {family.name}')
    print(f'Event: {event.name}')
    print(f'Housework: {housework.title if category else "No category"}')
else:
    print('No family found for user')