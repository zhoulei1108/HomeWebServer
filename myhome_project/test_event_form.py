from apps.events.forms import EventForm
from django.contrib.auth.models import User
from apps.family.models import get_current_family

user = User.objects.first()
family = get_current_family(user)

form_data = {
    'name': '测试事件',
    'event_type': 'one_time',
    'date_one_time': '2024-12-10'
}

form = EventForm(data=form_data, current_family=family)
print(f'表单验证: {form.is_valid()}')

if form.errors:
    print(f'错误: {form.errors}')
else:
    print('表单验证成功！')