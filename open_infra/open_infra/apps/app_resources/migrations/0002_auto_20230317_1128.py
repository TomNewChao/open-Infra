# Generated by Django 3.2.18 on 2023-03-17 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_resources', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hwcloudaccount',
            options={'verbose_name': '华为云账户', 'verbose_name_plural': '华为云账户'},
        ),
        migrations.AlterModelOptions(
            name='hwcloudeipinfo',
            options={'verbose_name': '华为云eip信息', 'verbose_name_plural': '华为云eip信息'},
        ),
        migrations.AlterModelOptions(
            name='hwcloudprojectinfo',
            options={'verbose_name': '华为云项目信息', 'verbose_name_plural': '华为云项目信息'},
        ),
    ]
