#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
django.setup()

from apps.housework.models import create_default_categories

if __name__ == '__main__':
    print("正在创建默认家务分类...")
    create_default_categories()
    print("默认家务分类创建完成！")