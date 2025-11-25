from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from datetime import date, timedelta, datetime
from calendar import monthcalendar, monthrange

from .models import Housework, HouseworkCategory, HouseworkTemplate, create_default_categories
from .forms import HouseworkForm, HouseworkCompleteForm, HouseworkTemplateForm, HouseworkFilterForm


def safe_render(request, template_name, context=None):
    """安全渲染模板"""
    if context is None:
        context = {}
    
    try:
        return render(request, template_name, context)
    except:
        hint = (
            f"缺少模板：{template_name}\\n"
            f"请在该 app 的 templates/housework/ 目录下创建对应的模板文件。"
        )
        return HttpResponse(hint, content_type="text/plain; charset=utf-8")


@login_required
def create_housework(request):
    """新建家务"""
    if request.method == 'POST':
        form = HouseworkForm(request.POST, current_user=request.user)
        if form.is_valid():
            housework = form.save()
            messages.success(request, f"家务 '{housework.title}' 已成功创建！")
            return redirect('housework:list')
        else:
            messages.error(request, "请修正表单中的错误后重试。")
    else:
        initial_data = {}
        if request.GET.get('template_id'):
            # 从模板创建
            template = get_object_or_404(HouseworkTemplate, pk=request.GET.get('template_id'))
            initial_data = {
                'title': template.title,
                'description': template.description,
                'category': template.category,
                'planned_duration': template.default_duration,
                'priority': template.priority,
                'frequency': template.frequency,
            }
        
        form = HouseworkForm(current_user=request.user, initial=initial_data)
    
    return safe_render(request, 'housework/create_housework.html', {
        'form': form,
        'title': '新建家务',
        'button_text': '创建家务'
    })


@login_required
def edit_housework(request, pk):
    """编辑家务"""
    housework = get_object_or_404(Housework, pk=pk)
    
    if request.method == 'POST':
        form = HouseworkForm(request.POST, instance=housework, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"家务 '{housework.title}' 已更新！")
            return redirect('housework:detail', pk=housework.pk)
        else:
            messages.error(request, "请修正表单中的错误后重试。")
    else:
        form = HouseworkForm(instance=housework, current_user=request.user)
    
    return safe_render(request, 'housework/edit_housework.html', {
        'form': form,
        'housework': housework,
        'title': f'编辑家务 - {housework.title}'
    })


@login_required
def housework_detail(request, pk):
    """家务详情"""
    housework = get_object_or_404(Housework, pk=pk)
    
    return safe_render(request, 'housework/housework_detail.html', {
        'housework': housework,
        'title': housework.title
    })


@login_required
def housework_list(request):
    """家务列表"""
    form = HouseworkFilterForm(request.GET)
    houseworks = Housework.objects.all()
    
    # 应用筛选
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        if cleaned_data.get('user'):
            houseworks = houseworks.filter(user=cleaned_data['user'])
        
        if cleaned_data.get('category'):
            houseworks = houseworks.filter(category=cleaned_data['category'])
        
        if cleaned_data.get('status'):
            houseworks = houseworks.filter(status=cleaned_data['status'])
        
        if cleaned_data.get('priority'):
            houseworks = houseworks.filter(priority=cleaned_data['priority'])
        
        if cleaned_data.get('date_from'):
            houseworks = houseworks.filter(planned_date__gte=cleaned_data['date_from'])
        
        if cleaned_data.get('date_to'):
            houseworks = houseworks.filter(planned_date__lte=cleaned_data['date_to'])
    
    # 排序
    houseworks = houseworks.select_related('user', 'category').order_by('planned_date', '-priority')
    
    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(houseworks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return safe_render(request, 'housework/housework_list.html', {
        'page_obj': page_obj,
        'filter_form': form,
        'title': '家务列表'
    })


@login_required
@require_POST
def complete_housework(request, pk):
    """完成家务"""
    housework = get_object_or_404(Housework, pk=pk)
    
    if request.method == 'POST':
        form = HouseworkCompleteForm(request.POST, instance=housework)
        if form.is_valid():
            actual_duration = form.cleaned_data['actual_duration']
            housework.mark_completed(actual_duration)
            messages.success(request, f"家务 '{housework.title}' 已标记为完成！")
        else:
            messages.error(request, "请填写实际耗时。")
    
    return redirect(request.META.get('HTTP_REFERER', 'housework:list'))


@login_required
@require_POST
def delete_housework(request, pk):
    """删除家务"""
    housework = get_object_or_404(Housework, pk=pk)
    
    if request.method == 'POST':
        housework_name = housework.title
        housework.delete()
        messages.success(request, f"家务 '{housework_name}' 已删除！")
    
    return redirect('housework:list')


@login_required
def statistics_view(request):
    """家务统计视图"""
    # 获取当前年月
    year = request.GET.get('year', date.today().year)
    month = request.GET.get('month', date.today().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = date.today().year
        month = date.today().month
    
    # 计算日期范围
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # 基础统计
    houseworks = Housework.objects.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date
    ).select_related('user', 'category')
    
    total_count = houseworks.count()
    completed_count = houseworks.filter(status='completed').count()
    pending_count = houseworks.filter(status='pending').count()
    in_progress_count = houseworks.filter(status='in_progress').count()
    
    # 按用户统计
    user_stats = houseworks.values('user__username').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        total_planned_time=Sum('planned_duration'),
        total_actual_time=Sum('actual_duration', filter=Q(status='completed'))
    ).order_by('-completed')
    
    # 按分类统计
    category_stats = houseworks.values('category__name', 'category__color', 'category__icon').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed'))
    ).order_by('-total')
    
    # 按日期统计（完成率）
    date_stats = []
    for day in range(1, end_date.day + 1):
        current_date = date(year, month, day)
        day_houseworks = houseworks.filter(planned_date=current_date)
        total_day = day_houseworks.count()
        completed_day = day_houseworks.filter(status='completed').count()
        
        date_stats.append({
            'date': current_date,
            'total': total_day,
            'completed': completed_day,
            'completion_rate': (completed_day / total_day * 100) if total_day > 0 else 0
        })
    
    # 效率分析
    completed_houseworks = houseworks.filter(status='completed', actual_duration__isnull=False)
    avg_time_diff = completed_houseworks.aggregate(
        avg_diff=Avg('actual_duration') - Avg('planned_duration')
    )['avg_diff'] or 0
    
    context = {
        'year': year,
        'month': month,
        'month_name': ['一月', '二月', '三月', '四月', '五月', '六月', 
                      '七月', '八月', '九月', '十月', '十一月', '十二月'][month-1],
        
        # 基础统计
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completion_rate': (completed_count / total_count * 100) if total_count > 0 else 0,
        
        # 详细统计
        'user_stats': user_stats,
        'category_stats': category_stats,
        'date_stats': date_stats,
        'avg_time_diff': avg_time_diff,
        
        'title': f'{year}年{month}月 家务统计'
    }
    
    return safe_render(request, 'housework/statistics.html', context)


@login_required
def get_month_houseworks(request):
    """获取指定月份的家务数据（用于月视图AJAX）"""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if not year or not month:
        return JsonResponse({'error': '缺少年月参数'}, status=400)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse({'error': '无效的年月参数'}, status=400)
    
    # 获取该月的家务数据
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    houseworks = Housework.objects.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date
    ).select_related('user', 'category')
    
    # 按日期分组
    houseworks_by_day = {}
    for housework in houseworks:
        day = housework.planned_date.day
        if day not in houseworks_by_day:
            houseworks_by_day[day] = []
        houseworks_by_day[day].append({
            'id': housework.id,
            'title': housework.title,
            'abbreviation': housework.abbreviation,
            'user_abbreviation': housework.user_abbreviation,
            'color': housework.display_color,
            'category_icon': housework.category.icon if housework.category else '🏠',
            'status': housework.status,
            'priority': housework.priority,
        })
    
    return JsonResponse({
        'houseworks_by_day': houseworks_by_day,
        'total_count': len(houseworks),
    })


# 模板相关视图
@login_required
def template_list(request):
    """家务模板列表"""
    templates = HouseworkTemplate.objects.all().select_related('category', 'created_by')
    
    return safe_render(request, 'housework/template_list.html', {
        'templates': templates,
        'title': '家务模板'
    })


@login_required
def create_template(request):
    """创建家务模板"""
    if request.method == 'POST':
        form = HouseworkTemplateForm(request.POST, current_user=request.user)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f"模板 '{template.title}' 已创建！")
            return redirect('housework:template_list')
        else:
            messages.error(request, "请修正表单中的错误后重试。")
    else:
        form = HouseworkTemplateForm(current_user=request.user)
    
    return safe_render(request, 'housework/create_template.html', {
        'form': form,
        'title': '创建家务模板'
    })