from django.shortcuts import render, redirect, get_object_or_404

from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Event
from .forms import EventForm, EventFilterForm

def safe_render(request, template_name, context=None):
    """
    安全渲染模板，如果模板不存在则返回友好提示
    """
    if context is None:
        context = {}
    
    try:
        return render(request, template_name, context)
    except TemplateDoesNotExist:
        hint = (
            f"缺少模板：{template_name}\n"
            f"请在该 app 的 templates/myhome/events/ 目录下创建对应的模板文件。\n"
            f"建议路径：e:/Develop/HomeWebServer/.venv_django/Scripts/myhome/apps/events/templates/{template_name}"
        )
        return HttpResponse(hint, content_type="text/plain; charset=utf-8")

@login_required
def create_event(request):
    """
    创建新事件
    GET: 显示创建表单
    POST: 处理表单提交
    """
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user)
    
    if request.method == "POST":
        form = EventForm(request.POST, current_family=current_family)
        if form.is_valid():
            try:
                # 检查用户是否有家庭
                if not current_family:
                    messages.error(request, '您还没有加入任何家庭，无法创建事件')
                    return redirect('family:create')
                
                # 自动关联创建者
                instance = form.save(commit=False)
                instance.creator = request.user
                instance.save()
                
                messages.success(request, f"事件 '{instance.name}' 已成功创建！")
                return redirect("events:event_detail", pk=instance.pk)
            except Exception as e:
                # 捕获模型验证错误
                error_messages = str(e)
                messages.error(request, f"保存事件时出错：{error_messages}")
        else:
            # 提供详细的错误信息
            error_details = []
            for field, errors in form.errors.items():
                field_name = form.fields[field].label if field in form.fields else field
                for error in errors:
                    error_details.append(f"{field_name}: {error}")
            
            # 添加非字段错误
            if form.non_field_errors():
                for error in form.non_field_errors():
                    error_details.append(f"表单错误: {error}")
            
            error_message = "请修正表单中的错误后重试：\n" + "\n".join(error_details)
            messages.error(request, error_message)
    else:
        # 预填充一些默认值
        initial_data = {}
        if request.GET.get('type'):
            initial_data['event_type'] = request.GET.get('type')
        form = EventForm(initial=initial_data)

    return safe_render(request, "myhome/events/create_event.html", {
        "form": form,
        "title": "创建新事件",
        "button_text": "创建事件"
    })

def event_detail(request, pk):
    """
    显示事件详情
    """
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user)
    
    event = get_object_or_404(Event, pk=pk)
    
    # 检查权限：用户只能查看自己家庭的事件
    if current_family and event.family != current_family:
        messages.error(request, '您没有权限查看该事件')
        return redirect('events:list')
    elif not current_family:
        messages.error(request, '您还没有加入任何家庭')
        return redirect('family:create')
    
    next_occurrence = event.next_occurrence()
    
    context = {
        "event": event,
        "next_occurrence": next_occurrence,
        "next_occurrence_display": event.next_occurrence_display,
        "title": event.name,
    }
    
    return safe_render(request, "myhome/events/event_detail.html", context)

def event_list(request):
    """
    事件列表视图，支持筛选和分页
    """
    try:
        # 获取当前用户的家庭
        from apps.family.models import get_current_family
        current_family = get_current_family(request.user)
        
        # 获取筛选参数
        filter_form = EventFilterForm(request.GET)
        
        # 只显示当前家庭的事件
        events = Event.objects.filter(family=current_family) if current_family else Event.objects.none()
        
        # 先过滤掉数据有问题的记录
        events = events.exclude(active__isnull=True)
        
        # 先过滤掉数据有问题的记录
        events = events.exclude(active__isnull=True)
        
        # 应用筛选
        if filter_form.is_valid():
            cleaned_data = filter_form.cleaned_data
            
            # 按类型筛选
            event_type = cleaned_data.get('event_type')
            if event_type:
                events = events.filter(event_type=event_type)
            
            # 按状态筛选
            active = cleaned_data.get('active')
            if active:
                events = events.filter(active=(active == 'true'))
            
            # 按日期范围筛选
            date_from = cleaned_data.get('date_from')
            date_to = cleaned_data.get('date_to')
            if date_from:
                events = events.filter(date__gte=date_from)
            if date_to:
                events = events.filter(date__lte=date_to)
        
        # 搜索功能
        search_query = request.GET.get('search', '').strip()
        if search_query:
            events = events.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # 排序 - 避免按active字段排序
        sort_by = request.GET.get('sort', '-created_at')
        allowed_sort_fields = ['name', 'created_at', 'updated_at', 'priority', 'date']
        if sort_by and sort_by.lstrip('-') in allowed_sort_fields:
            events = events.order_by(sort_by)
        
        # 分页
        paginator = Paginator(events, 20)  # 每页20条
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "search_query": search_query,
            "sort_by": sort_by,
            "title": "事件列表",
        }
        
        return safe_render(request, "myhome/events/event_list.html", context)
        
    except Exception as e:
        # 记录错误并返回简单的列表
        messages.error(request, f"加载事件列表时出错: {str(e)}")
        events = Event.objects.filter(active=True).order_by('-created_at')
        paginator = Paginator(events, 20)
        page_obj = paginator.get_page(1)
        
        context = {
            "page_obj": page_obj,
            "filter_form": EventFilterForm(),
            "search_query": "",
            "sort_by": "-created_at",
            "title": "事件列表",
        }
        
        return safe_render(request, "myhome/events/event_list.html", context)

@login_required
def toggle_event_status(request, pk):
    """
    切换事件启用/禁用状态
    """
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user)
    
    event = get_object_or_404(Event, pk=pk)
    
    # 检查权限：用户只能操作自己家庭的事件
    if current_family and event.family != current_family:
        messages.error(request, '您没有权限操作该事件')
        return redirect('events:list')
    elif not current_family:
        messages.error(request, '您还没有加入任何家庭')
        return redirect('family:create')
    
    event.active = not event.active
    event.save()
    
    status_text = "启用" if event.active else "禁用"
    messages.success(request, f"事件 '{event.name}' 已{status_text}。")
    
    # 如果是AJAX请求，返回JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            "success": True,
            "active": event.active,
            "message": f"事件已{status_text}"
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'events:event_list'))

@login_required
def upcoming_events(request):
    """
    显示即将到来的事件
    """
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user)
    
    days = int(request.GET.get('days', 30))  # 默认显示未来30天
    if days < 1 or days > 365:
        days = 30
    
    # 只显示当前家庭的即将到来的事件
    if current_family:
        events = Event.objects.filter(family=current_family).active()
        # 手动过滤即将到来的事件，因为自定义管理器可能不支持链式过滤
        from django.utils import timezone
        cutoff_date = timezone.now() + timezone.timedelta(days=days)
        events = events.filter(date__lte=cutoff_date).order_by('date')
    else:
        events = Event.objects.none()
    
    context = {
        "events": events,
        "days": days,
        "title": f"未来{days}天内的事件",
    }
    
    return safe_render(request, "myhome/events/upcoming_events.html", context)

@login_required
def delete_event(request, pk):
    """
    删除事件
    """
    # 获取当前用户的家庭
    from apps.family.models import get_current_family
    current_family = get_current_family(request.user)
    
    event = get_object_or_404(Event, pk=pk)
    
    # 检查权限：用户只能删除自己家庭的事件
    if current_family and event.family != current_family:
        messages.error(request, '您没有权限删除该事件')
        return redirect('events:list')
    elif not current_family:
        messages.error(request, '您还没有加入任何家庭')
        return redirect('family:create')
    
    if request.method == "POST":
        event_name = event.name
        event.delete()
        messages.success(request, f"事件 '{event_name}' 已成功删除！")
        
        # 如果是AJAX请求，返回JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                "success": True,
                "message": f"事件 '{event_name}' 已删除"
            })
        
        return redirect("events:list")
    
    # GET请求显示确认页面
    context = {
        "event": event,
        "title": "删除事件",
    }
    
    return safe_render(request, "myhome/events/delete_confirm.html", context)

def create_success(request):
    """
    创建成功页面（保持向后兼容）
    """
    return safe_render(request, "myhome/events/create_success.html", {
        "title": "创建成功"
    })