from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
import uuid


class Family(models.Model):
    """家庭组模型"""
    
    name = models.CharField("家庭名称", max_length=100)
    description = models.TextField("家庭描述", blank=True, help_text="描述一下您的家庭特色")
    invite_code = models.UUIDField("邀请码", default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    # 家庭设置
    max_members = models.PositiveIntegerField("最大成员数", default=10, help_text="家庭组最大成员数量")
    is_public = models.BooleanField("公开家庭组", default=False, help_text="是否允许搜索到本家庭组")
    
    # 装饰性字段
    avatar = models.ImageField("家庭头像", upload_to='family_avatars/', blank=True, null=True)
    color_theme = models.CharField("主题色", max_length=7, default="#a8edea", help_text="十六进制颜色代码")
    
    class Meta:
        verbose_name = "家庭组"
        verbose_name_plural = "家庭组"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        """获取成员数量"""
        return self.members.count()
    
    def get_active_members(self):
        """获取活跃成员"""
        return self.members.filter(is_active=True)
    
    def get_admin_members(self):
        """获取管理员成员"""
        return self.members.filter(role='admin')
    
    def is_member(self, user):
        """检查用户是否是家庭成员"""
        return self.members.filter(user=user, is_active=True).exists()
    
    def get_member_role(self, user):
        """获取用户在家庭中的角色"""
        try:
            member = self.members.get(user=user, is_active=True)
            return member.role
        except FamilyMember.DoesNotExist:
            return None
    
    def can_user_join(self, user):
        """检查用户是否可以加入家庭"""
        if self.is_member(user):
            return False, "您已经是该家庭的成员"
        
        if self.get_member_count() >= self.max_members:
            return False, f"该家庭成员已达上限({self.max_members}人)"
            
        return True, "可以加入"
    
    def clean(self):
        """验证数据"""
        if self.max_members < 2:
            raise ValidationError("家庭成员数不能少于2人")


class FamilyMember(models.Model):
    """家庭成员模型"""
    
    ROLE_CHOICES = [
        ('owner', '家庭主'),
        ('admin', '管理员'),
        ('member', '成员'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_memberships', verbose_name="用户")
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members', verbose_name="家庭")
    
    role = models.CharField("角色", max_length=10, choices=ROLE_CHOICES, default='member')
    nickname = models.CharField("家庭昵称", max_length=50, blank=True, help_text="在家庭中的显示名称")
    is_active = models.BooleanField("是否激活", default=True)
    joined_at = models.DateTimeField("加入时间", auto_now_add=True)
    last_active = models.DateTimeField("最后活跃", auto_now=True)
    
    # 权限设置
    can_create_events = models.BooleanField("可创建事件", default=True)
    can_create_housework = models.BooleanField("可创建家务", default=True)
    can_invite_members = models.BooleanField("可邀请成员", default=False)
    can_manage_family = models.BooleanField("可管理家庭", default=False)
    
    class Meta:
        verbose_name = "家庭成员"
        verbose_name_plural = "家庭成员"
        unique_together = ['user', 'family']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['user', 'family']),
            models.Index(fields=['family', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.family.name}"
    
    @property
    def display_name(self):
        """获取显示名称"""
        return self.nickname or self.user.username
    
    def get_permissions(self):
        """获取用户权限列表"""
        permissions = []
        if self.can_create_events:
            permissions.append('create_events')
        if self.can_create_housework:
            permissions.append('create_housework')
        if self.can_invite_members:
            permissions.append('invite_members')
        if self.can_manage_family:
            permissions.append('manage_family')
        return permissions
    
    def has_permission(self, permission):
        """检查是否有特定权限"""
        return getattr(self, f'can_{permission}', False)
    
    def save(self, *args, **kwargs):
        # 家庭主拥有所有权限
        if self.role == 'owner':
            self.can_create_events = True
            self.can_create_housework = True
            self.can_invite_members = True
            self.can_manage_family = True
        # 管理员拥有大部分权限
        elif self.role == 'admin':
            self.can_create_events = True
            self.can_create_housework = True
            self.can_invite_members = True
            self.can_manage_family = False
        
        super().save(*args, **kwargs)


class Invitation(models.Model):
    """邀请模型"""
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期'),
    ]
    
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='invitations', verbose_name="家庭")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name="邀请人")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations', verbose_name="被邀请人")
    
    status = models.CharField("状态", max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField("邀请消息", blank=True, help_text="对被邀请人的留言")
    
    created_at = models.DateTimeField("邀请时间", auto_now_add=True)
    responded_at = models.DateTimeField("回复时间", null=True, blank=True)
    
    # 过期时间（7天后过期）
    expires_at = models.DateTimeField("过期时间")
    
    class Meta:
        verbose_name = "邀请"
        verbose_name_plural = "邀请"
        unique_together = ['family', 'invitee']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invitee', 'status']),
            models.Index(fields=['family', 'status']),
        ]
    
    def __str__(self):
        return f"{self.inviter.username} 邀请 {self.invitee.username} 加入 {self.family.name}"
    
    def save(self, *args, **kwargs):
        # 设置过期时间为7天后
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """检查邀请是否过期"""
        return timezone.now() > self.expires_at
    
    def can_respond(self):
        """检查是否可以回复邀请"""
        return self.status == 'pending' and not self.is_expired()
    
    def accept(self):
        """接受邀请"""
        if not self.can_respond():
            return False, "邀请已过期或已处理"
        
        # 检查是否可以加入家庭
        can_join, message = self.family.can_user_join(self.invitee)
        if not can_join:
            return False, message
        
        try:
            # 创建家庭成员记录
            FamilyMember.objects.create(
                family=self.family,
                user=self.invitee,
                role='member'
            )
            
            # 设置用户的当前家庭
            set_current_family(self.invitee, self.family)
            
            # 更新邀请状态
            self.status = 'accepted'
            self.responded_at = timezone.now()
            self.save()
            
            return True, "成功加入家庭"
        except Exception as e:
            return False, f"加入家庭失败: {str(e)}"
    
    def reject(self):
        """拒绝邀请"""
        if not self.can_respond():
            return False, "邀请已过期或已处理"
        
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
        return True, "已拒绝邀请"


class UserProfile(models.Model):
    """用户扩展信息"""
    
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
        ('P', '不愿透露'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_profile', verbose_name="用户")
    current_family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='current_users', verbose_name="当前家庭")
    
    # 个人基本信息
    avatar = models.ImageField("头像", upload_to='user_avatars/', blank=True, null=True)
    nickname = models.CharField("昵称", max_length=50, blank=True, help_text="在系统中显示的昵称")
    gender = models.CharField("性别", max_length=1, choices=GENDER_CHOICES, blank=True, default='P')
    birthday = models.DateField("生日", null=True, blank=True)
    bio = models.TextField("个人简介", blank=True, max_length=500, help_text="介绍一下自己")
    
    # 个人偏好
    favorite_color = models.CharField("喜欢的颜色", max_length=7, blank=True, default="#a8edea", 
                                   help_text="十六进制颜色代码")
    favorite_food = models.CharField("爱吃的食物", max_length=200, blank=True, 
                                   help_text="比如：火锅、烤肉、寿司等")
    hobbies = models.TextField("个人爱好", blank=True, max_length=500, 
                            help_text="比如：阅读、运动、音乐、旅行等")
    
    # 联系信息
    phone = models.CharField("手机号", max_length=20, blank=True)
    address = models.CharField("地址", max_length=200, blank=True)
    
    # 设置偏好
    notification_enabled = models.BooleanField("启用通知", default=True)
    email_notifications = models.BooleanField("邮件通知", default=True)
    public_profile = models.BooleanField("公开个人资料", default=False, 
                                     help_text="是否允许其他家庭成员查看您的详细资料")
    
    # 时间戳
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    class Meta:
        verbose_name = "用户档案"
        verbose_name_plural = "用户档案"
    
    def __str__(self):
        return f"{self.display_name} 的档案"
    
    @property
    def display_name(self):
        """获取显示名称"""
        return self.nickname or self.user.username
    
    @property
    def has_family(self):
        """检查是否有家庭"""
        return self.current_family is not None
    
    @property
    def family_role(self):
        """获取在家庭中的角色"""
        if not self.current_family:
            return None
        return self.current_family.get_member_role(self.user)
    
    @property
    def avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return self.avatar.url
        # 默认头像（使用Gravatar或其他服务）
        return f"https://ui-avatars.com/api/?name={self.display_name}&background=random"
    
    @property
    def age(self):
        """计算年龄"""
        if self.birthday:
            from datetime import date
            today = date.today()
            return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return None


def get_user_families(user):
    """获取用户的所有家庭"""
    return Family.objects.filter(
        members__user=user,
        members__is_active=True
    ).distinct()


def get_current_family(user):
    """获取用户的当前家庭"""
    try:
        profile = user.family_profile
        return profile.current_family
    except UserProfile.DoesNotExist:
        # 创建用户档案
        UserProfile.objects.create(user=user)
        return None


def set_current_family(user, family):
    """设置用户的当前家庭"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    if family and family.is_member(user):
        profile.current_family = family
    else:
        profile.current_family = None
    profile.save()
    return profile


def switch_family(user, family_id):
    """切换家庭"""
    try:
        family = Family.objects.get(id=family_id)
        if family.is_member(user):
            set_current_family(user, family)
            return True, f"已切换到家庭: {family.name}"
        else:
            return False, "您不是该家庭的成员"
    except Family.DoesNotExist:
        return False, "家庭不存在"