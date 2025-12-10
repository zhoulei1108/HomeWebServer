from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, FamilyMember, Invitation


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时自动创建用户档案"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=FamilyMember)
def update_family_last_active(sender, instance, created, **kwargs):
    """家庭成员活跃时更新最后活跃时间"""
    if created:
        # 新成员加入，更新家庭
        instance.family.save()


@receiver(pre_delete, sender=FamilyMember)
def cleanup_member_data(sender, instance, **kwargs):
    """成员离开时清理相关数据"""
    # 如果该用户将此家庭设为当前家庭，清除设置
    try:
        profile = instance.user.family_profile
        if profile.current_family == instance.family:
            profile.current_family = None
            profile.save()
    except UserProfile.DoesNotExist:
        pass