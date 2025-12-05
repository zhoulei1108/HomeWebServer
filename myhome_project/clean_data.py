#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhome.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.housework.models import Housework

Housework.objects.all().delete()
print('清理完成')