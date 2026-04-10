#!/usr/bin/env python
"""
Django 命令行管理工具
提供 Django 项目的各种管理命令：runserver, migrate, shell 等

使用方法:
  python manage.py <command> [options]
  
常用命令:
  runserver    - 启动开发服务器
  migrate      - 执行数据库迁移
  makemigrations - 创建数据库迁移文件
  shell        - 启动 Django 交互式 shell
  createsuperuser - 创建超级用户
  collectstatic - 收集静态文件
"""
import os
import sys


def main():
    """
    执行 Django 管理命令
    
    功能:
    1. 设置 Django 配置文件路径
    2. 加载 Django 管理命令执行器
    3. 处理命令行参数并执行相应命令
    """
    # 设置 Django 配置模块
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myhome.settings")
    
    try:
        # 导入 Django 的命令行执行器
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 处理 Django 未安装或环境配置错误的情况
        raise ImportError(
            "无法导入 Django。请确认:\n"
            "1. Django 已正确安装\n"
            "2. Python 虚拟环境已激活\n"
            "3. 项目在 PYTHONPATH 中\n"
            "4. 是否忘记了激活虚拟环境？"
        ) from exc
    
    # 执行传入的命令行参数
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    """
    脚本入口点
    直接调用 main() 函数执行管理命令
    """
    main()
