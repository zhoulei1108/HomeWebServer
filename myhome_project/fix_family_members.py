"""
修复家庭成员的当前家庭设置
确保所有家庭成员都有正确的当前家庭
"""
from django.contrib.auth.models import User
from apps.family.models import FamilyMember, get_current_family, set_current_family

def fix_family_members():
    print("=== 修复家庭成员当前家庭设置 ===")
    
    # 获取所有家庭成员
    members = FamilyMember.objects.filter(is_active=True)
    print(f"找到 {members.count()} 个活跃的家庭成员")
    
    fixed_count = 0
    for member in members:
        current_family = get_current_family(member.user)
        if current_family != member.family:
            print(f"修复用户 {member.user.username}: 当前家庭 {current_family.name if current_family else 'None'} -> 应该是 {member.family.name}")
            set_current_family(member.user, member.family)
            fixed_count += 1
        else:
            print(f"用户 {member.user.username} 当前家庭正确: {member.family.name}")
    
    print(f"\n总共修复了 {fixed_count} 个用户的当前家庭设置")
    
    # 验证修复结果
    print("\n=== 验证修复结果 ===")
    for member in members:
        current_family = get_current_family(member.user)
        status = "✅ 正确" if current_family == member.family else "❌ 错误"
        print(f"{status} {member.user.username}: {member.family.name} ({current_family.name if current_family else 'None'})")

if __name__ == '__main__':
    fix_family_members()