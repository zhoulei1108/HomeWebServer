#!/usr/bin/env python
"""
测试登录功能的脚本
"""
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_login():
    """测试登录功能"""
    print("🔍 测试登录功能...")
    
    # 检查用户是否存在
    try:
        user = User.objects.get(username='admin')
        print(f"✅ 管理员用户存在: {user.username}")
    except User.DoesNotExist:
        print("❌ 管理员用户不存在")
        return False
    
    # 测试登录
    client = Client()
    
    # 测试访问需要登录的页面
    response = client.get('/calendar/event/new/')
    if response.status_code == 302:  # 重定向到登录页面
        print("✅ 未登录时正确重定向到登录页面")
    else:
        print(f"❌ 未登录时未正确重定向，状态码: {response.status_code}")
        return False
    
    # 测试登录
    response = client.post('/accounts/login/', {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': 'test'
    })
    
    if response.status_code == 302:  # 登录成功重定向
        print("✅ 登录成功，正确重定向")
    else:
        print(f"❌ 登录失败，状态码: {response.status_code}")
        return False
    
    # 测试登录后访问受保护页面
    client.login(username='admin', password='admin123')
    response = client.get('/calendar/event/new/')
    if response.status_code == 200:  # 可以正常访问
        print("✅ 登录后可以访问受保护页面")
    else:
        print(f"❌ 登录后无法访问受保护页面，状态码: {response.status_code}")
        return False
    
    print("\n🎉 所有登录功能测试通过！")
    return True

if __name__ == '__main__':
    success = test_login()
    if success:
        print("\n📋 使用说明:")
        print("1. 启动服务器: python manage.py runserver")
        print("2. 访问: http://127.0.0.1:8000/accounts/login/")
        print("3. 使用管理员账户登录:")
        print("   - 用户名: admin")
        print("   - 密码: admin123")
        print("4. 登录后可以创建和管理事件")