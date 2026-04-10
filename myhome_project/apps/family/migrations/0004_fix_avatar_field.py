<<<<<<< HEAD
# Generated migration to fix avatar field type mismatch
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('family', '0003_auto_20251209_2023'),
    ]

    operations = [
        # 修改avatar字段为正确的ImageField类型，允许为空
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='user_avatars/', verbose_name='头像'),
        ),
=======
# Generated migration to fix avatar field type mismatch
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('family', '0003_auto_20251209_2023'),
    ]

    operations = [
        # 修改avatar字段为正确的ImageField类型，允许为空
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='user_avatars/', verbose_name='头像'),
        ),
>>>>>>> 09e3bc1e4536a9fbe86e3310ebd075b695fa1962
    ]