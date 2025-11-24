#!/usr/bin/env python
"""
测试表单验证的简单脚本
"""
import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.venv_django', 'Scripts', 'myhome', 'apps'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.events.forms import EventFilterForm

def test_filter_form():
    """测试筛选表单"""
    print("测试 EventFilterForm...")
    
    # 测试空数据
    form = EventFilterForm(data={})
    print(f"空数据验证: {form.is_valid()}")
    if form.errors:
        print(f"错误: {form.errors}")
    
    # 测试包含空字符串的active字段
    form = EventFilterForm(data={'active': ''})
    print(f"active='': {form.is_valid()}")
    if form.errors:
        print(f"错误: {form.errors}")
    else:
        print(f"cleaned_data: {form.cleaned_data}")
    
    # 测试active=True
    form = EventFilterForm(data={'active': 'True'})
    print(f"active='True': {form.is_valid()}")
    if form.errors:
        print(f"错误: {form.errors}")
    else:
        print(f"cleaned_data: {form.cleaned_data}")
    
    # 测试active=False
    form = EventFilterForm(data={'active': 'False'})
    print(f"active='False': {form.is_valid()}")
    if form.errors:
        print(f"错误: {form.errors}")
    else:
        print(f"cleaned_data: {form.cleaned_data}")

if __name__ == '__main__':
    test_filter_form()
    print("测试完成！")