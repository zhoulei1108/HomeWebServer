from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from .models import LinkCategory, CustomLink
from .forms import LinkCategoryForm, CustomLinkForm


def toolbox_index(request):
    """百宝箱主页 - 显示所有分类和链接"""
    categories = LinkCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('links', queryset=CustomLink.objects.filter(is_active=True).order_by('order'))
    ).order_by('order')
    
    context = {
        'categories': categories,
        'page_title': '百宝箱',
    }
    return render(request, 'toolbox/index.html', context)


@login_required
def category_create(request):
    """创建分类"""
    if request.method == 'POST':
        form = LinkCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'分类 "{category.name}" 创建成功！')
            return redirect('toolbox:index')
    else:
        form = LinkCategoryForm()
    
    context = {
        'form': form,
        'page_title': '创建分类',
    }
    return render(request, 'toolbox/category_form.html', context)


@login_required
def category_edit(request, pk):
    """编辑分类"""
    category = get_object_or_404(LinkCategory, pk=pk)
    
    if request.method == 'POST':
        form = LinkCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'分类 "{category.name}" 更新成功！')
            return redirect('toolbox:index')
    else:
        form = LinkCategoryForm(instance=category)
    
    context = {
        'form': form,
        'page_title': '编辑分类',
        'category': category,
    }
    return render(request, 'toolbox/category_form.html', context)


@login_required
def category_delete(request, pk):
    """删除分类"""
    category = get_object_or_404(LinkCategory, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'分类 "{category_name}" 删除成功！')
        return redirect('toolbox:index')
    
    context = {
        'category': category,
        'page_title': '删除分类',
    }
    return render(request, 'toolbox/category_confirm_delete.html', context)


@login_required
def link_create(request):
    """创建链接"""
    if request.method == 'POST':
        form = CustomLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.created_by = request.user
            link.save()
            messages.success(request, f'链接 "{link.title}" 创建成功！')
            return redirect('toolbox:index')
    else:
        form = CustomLinkForm()
    
    context = {
        'form': form,
        'page_title': '创建链接',
    }
    return render(request, 'toolbox/link_form.html', context)


@login_required
def link_edit(request, pk):
    """编辑链接"""
    link = get_object_or_404(CustomLink, pk=pk)
    
    if request.method == 'POST':
        form = CustomLinkForm(request.POST, instance=link)
        if form.is_valid():
            link = form.save()
            messages.success(request, f'链接 "{link.title}" 更新成功！')
            return redirect('toolbox:index')
    else:
        form = CustomLinkForm(instance=link)
    
    context = {
        'form': form,
        'page_title': '编辑链接',
        'link': link,
    }
    return render(request, 'toolbox/link_form.html', context)


@login_required
def link_delete(request, pk):
    """删除链接"""
    link = get_object_or_404(CustomLink, pk=pk)
    
    if request.method == 'POST':
        link_title = link.title
        link.delete()
        messages.success(request, f'链接 "{link_title}" 删除成功！')
        return redirect('toolbox:index')
    
    context = {
        'link': link,
        'page_title': '删除链接',
    }
    return render(request, 'toolbox/link_confirm_delete.html', context)
