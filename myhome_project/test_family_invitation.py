"""
测试邀请接受流程
"""
from django.contrib.auth.models import User
from apps.family.models import Family, FamilyMember, Invitation, get_current_family

def test_invitation_flow():
    print("=== 测试邀请接受流程 ===")
    
    # 获取测试用户
    inviter = User.objects.get(username='zhoulei')
    invitee = User.objects.get(username='test03')
    family = get_current_family(inviter)
    
    print(f"邀请人: {inviter.username}, 家庭: {family.name}")
    print(f"被邀请人: {invitee.username}")
    
    # 检查邀请前状态
    before_family = get_current_family(invitee)
    print(f"邀请前被邀请人的当前家庭: {before_family.name if before_family else 'None'}")
    
    # 创建邀请
    invitation = Invitation.objects.create(
        family=family,
        inviter=inviter,
        invitee=invitee,
        message='欢迎加入我们的家庭'
    )
    print(f"创建邀请: {invitation}")
    
    # 接受邀请
    success, message = invitation.accept()
    print(f"接受邀请结果: {success}, 消息: {message}")
    
    # 检查邀请后状态
    after_family = get_current_family(invitee)
    print(f"邀请后被邀请人的当前家庭: {after_family.name if after_family else 'None'}")
    
    # 检查家庭成员记录
    member = FamilyMember.objects.filter(user=invitee, family=family, is_active=True).first()
    if member:
        print(f"家庭成员记录: 角色={member.role}, 可创建事件={member.can_create_events}")
    else:
        print("❌ 没有找到家庭成员记录")
    
    print("=== 测试完成 ===")

if __name__ == '__main__':
    test_invitation_flow()