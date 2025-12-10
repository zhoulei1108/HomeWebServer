# Generated manually to add missing fields to UserProfile

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('family', '0002_auto_20251209_1653'),
    ]

    operations = [
        # Add missing fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='user_avatars/', verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nickname',
            field=models.CharField(blank=True, help_text='在系统中显示的昵称', max_length=50, verbose_name='昵称'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', '男'), ('F', '女'), ('O', '其他'), ('P', '不愿透露')], default='P', max_length=1, verbose_name='性别'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='生日'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, help_text='介绍一下自己', max_length=500, verbose_name='个人简介'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='favorite_color',
            field=models.CharField(blank=True, default='#a8edea', help_text='十六进制颜色代码', max_length=7, verbose_name='喜欢的颜色'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='favorite_food',
            field=models.CharField(blank=True, help_text='比如：火锅、烤肉、寿司等', max_length=200, verbose_name='爱吃的食物'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='hobbies',
            field=models.TextField(blank=True, help_text='比如：阅读、运动、音乐、旅行等', max_length=500, verbose_name='个人爱好'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='手机号'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, max_length=200, verbose_name='地址'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='public_profile',
            field=models.BooleanField(default=False, help_text='是否允许其他家庭成员查看您的详细资料', verbose_name='公开个人资料'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
    ]