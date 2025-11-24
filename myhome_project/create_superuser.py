#!/usr/bin/env python
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """创建管理员用户"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✅ 成功创建管理员用户:")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   密码: {password}")
        print(f"\n🔗 登录地址: http://127.0.0.1:8000/accounts/login/")
    else:
        print(f"❌ 用户 '{username}' 已存在")

if __name__ == '__main__':
    create_admin_user()