from apps.family.models import Invitation
from django.contrib.auth.models import User

user = User.objects.get(username='test02')
invitations = Invitation.objects.filter(invitee=user)
print(f'{user.username} 的邀请:')
for inv in invitations:
    print(f'  - ID: {inv.id}, 家庭: {inv.family.name}, 状态: {inv.status}, 创建时间: {inv.created_at}')