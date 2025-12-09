from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.db import transaction, models
from django.core.paginator import Paginator
from .models import Family, FamilyMember, UserProfile, Invitation, get_current_family
from .forms import UserProfileForm, ProfileSettingsForm
import json
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        
        if user and user.check_password(password):
            login(request, user)
            
            # 设置当前家庭
            current_family = get_current_family(user)
            if current_family:
                messages.success(request, f'欢迎回来，{user.username}！')
                return redirect('family:dashboard')
            else:
                messages.info(request, '请创建或加入一个家庭')
                return redirect('family:create')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'registration/login.html')


@login_required
def dashboard(request):
    """家庭中心仪表板"""
    user = request.user
    
    # 尝试自动设置当前家庭
    current_family = get_current_family(user)
    
    # 如果没有当前家庭，尝试设置用户的第一个家庭
    if not current_family:
        first_family = Family.objects.filter(
            members__user=user, 
            members__is_active=True
        ).first()
        
        if first_family:
            from .models import set_current_family
            set_current_family(user, first_family)
            current_family = first_family
    
    # 获取家庭信息
    family_info = None
    members = []
    recent_invitations = []
    
    if current_family:
        family_info = {
            'family': current_family,
            'member_count': current_family.get_member_count(),
            'role': current_family.get_member_role(user),
        }
        
        # 获取家庭成员
        members = FamilyMember.objects.filter(
            family=current_family,
            is_active=True
        ).select_related('user').order_by('-joined_at')
        
        # 获取最近的邀请
        recent_invitations = Invitation.objects.filter(
            invitee=user,
            status='pending'
        ).order_by('-created_at')[:5]
    
    context = {
        'family_info': family_info,
        'members': members,
        'recent_invitations': recent_invitations,
        'user_families': Family.objects.filter(
            members__user=user,
            members__is_active=True
        ).distinct(),
    }
    
    return render(request, 'family/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """个人资料查看和编辑"""
    user = request.user
    
    # 获取或创建用户档案
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料更新成功！')
            return redirect('family:profile')
        else:
            messages.error(request, '请检查填写的信息是否正确')
    else:
        form = UserProfileForm(instance=profile)
    
    # 获取用户统计信息
    user_stats = {
        'families_count': Family.objects.filter(
            members__user=user,
            members__is_active=True
        ).count(),
        'invitations_sent': Invitation.objects.filter(inviter=user).count(),
        'invitations_received': Invitation.objects.filter(invitee=user).count(),
    }
    
    context = {
        'form': form,
        'profile': profile,
        'user_stats': user_stats,
        'current_family': get_current_family(user),
    }
    
    return render(request, 'family/profile.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_settings(request):
    """个人设置页面"""
    user = request.user
    
    # 获取用户档案
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '设置保存成功！')
            return redirect('family:profile_settings')
        else:
            messages.error(request, '请检查填写的信息')
    else:
        form = ProfileSettingsForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'current_family': get_current_family(user),
    }
    
    return render(request, 'family/profile_settings.html', context)


@login_required
def profile_public(request, user_id):
    """公开的个人资料页面"""
    if not user_id:
        raise Http404("用户不存在")
    
    # 获取目标用户
    target_user = get_object_or_404(User, id=user_id)
    
    # 获取目标用户档案
    target_profile = get_object_or_404(UserProfile, user=target_user)
    
    # 检查是否可以查看
    current_user = request.user
    current_family = get_current_family(current_user) if current_user.is_authenticated else None
    
    can_view = False
    if target_profile.public_profile:
        # 公开资料，任何人可查看
        can_view = True
    elif current_user.is_authenticated and current_family:
        # 检查是否在同一个家庭
        if current_family.members.filter(user=target_user, is_active=True).exists():
            can_view = True
    
    if not can_view:
        messages.error(request, '您没有权限查看该用户的个人资料')
        return redirect('family:dashboard')
    
    context = {
        'target_profile': target_profile,
        'is_same_family': can_view and current_family,
        'current_family': current_family,
    }
    
    return render(request, 'family/profile_public.html', context)


@login_required
def switch_family(request, family_id):
    """切换当前家庭"""
    try:
        from .models import switch_family as do_switch
        success, message = do_switch(request.user, family_id)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
            
    except Exception as e:
        messages.error(request, f'切换家庭失败: {str(e)}')
    
    return redirect('family:dashboard')


@login_required
def create_family(request):
    """创建家庭"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        max_members = request.POST.get('max_members', 10)
        
        if name:
            try:
                with transaction.atomic():
                    # 创建家庭
                    family = Family.objects.create(
                        name=name,
                        description=description,
                        max_members=max_members
                    )
                    
                    # 创建者为家庭主
                    FamilyMember.objects.create(
                        family=family,
                        user=request.user,
                        role='owner'
                    )
                    
                    # 设置为当前家庭
                    from .models import set_current_family
                    set_current_family(request.user, family)
                    
                messages.success(request, f'家庭 "{name}" 创建成功！')
                return redirect('family:dashboard')
                
            except Exception as e:
                messages.error(request, f'创建家庭失败: {str(e)}')
        else:
            messages.error(request, '请输入家庭名称')
    
    return render(request, 'family/create_family.html')


@login_required
def search_family(request):
    """搜索家庭"""
    query = request.GET.get('q', '')
    families = []
    
    if query:
        families = Family.objects.filter(
            name__icontains=query,
            is_public=True
        ).annotate(member_count=models.Count('members'))
    
    context = {
        'families': families,
        'query': query,
    }
    
    return render(request, 'family/search_family.html', context)


@login_required
def send_invitation(request):
    """发送邀请"""
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message', '')
        family_id = request.POST.get('family_id')
        
        if not email:
            messages.error(request, '请输入被邀请人的邮箱')
            return redirect('family:dashboard')
        
        try:
            # 查找用户
            invitee = User.objects.get(email=email)
            
            # 检查是否已经是家庭成员
            current_family = get_current_family(request.user)
            if not current_family:
                messages.error(request, '请先加入或创建一个家庭')
                return redirect('family:dashboard')
            
            if current_family.is_member(invitee):
                messages.error(request, f'{invitee.username} 已经是家庭成员了')
                return redirect('family:dashboard')
            
            # 检查是否有待处理的邀请
            existing_invitation = Invitation.objects.filter(
                family=current_family,
                invitee=invitee,
                status='pending'
            ).first()
            
            if existing_invitation:
                messages.info(request, f'已经向 {invitee.username} 发送过邀请')
                return redirect('family:dashboard')
            
            # 创建邀请
            Invitation.objects.create(
                family=current_family,
                inviter=request.user,
                invitee=invitee,
                message=message
            )
            
            messages.success(request, f'邀请已发送给 {invitee.username}')
            
        except User.DoesNotExist:
            messages.error(request, '系统中没有找到该邮箱对应的用户')
        except Exception as e:
            messages.error(request, f'发送邀请失败: {str(e)}')
    
    return redirect('family:dashboard')


@login_required
def accept_invitation(request, invitation_id):
    """接受邀请"""
    invitation = get_object_or_404(Invitation, id=invitation_id)
    
    if invitation.invitee != request.user:
        messages.error(request, '您不能接受这个邀请')
        return redirect('family:dashboard')
    
    success, message = invitation.accept()
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('family:dashboard')


@login_required
def reject_invitation(request, invitation_id):
    """拒绝邀请"""
    invitation = get_object_or_404(Invitation, id=invitation_id)
    
    if invitation.invitee != request.user:
        messages.error(request, '您不能拒绝这个邀请')
        return redirect('family:dashboard')
    
    success, message = invitation.reject()
    
    if success:
        messages.info(request, message)
    else:
        messages.error(request, message)
    
    return redirect('family:dashboard')


@login_required
def invitations(request):
    """邀请列表"""
    user = request.user
    
    # 发送的邀请
    sent_invitations = Invitation.objects.filter(
        inviter=user
    ).order_by('-created_at')
    
    # 接收的邀请
    received_invitations = Invitation.objects.filter(
        invitee=user
    ).order_by('-created_at')
    
    context = {
        'sent_invitations': sent_invitations,
        'received_invitations': received_invitations,
        'current_family': get_current_family(user),
    }
    
    return render(request, 'family/invitations.html', context)