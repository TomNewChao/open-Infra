# Generated by Django 3.2.18 on 2023-03-16 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HWCloudHighRiskPort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.IntegerField(verbose_name='高危端口')),
                ('desc', models.CharField(max_length=255, verbose_name='高危端口')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '华为云高危端口',
                'db_table': 'hw_cloud_high_risk_port',
            },
        ),
        migrations.CreateModel(
            name='HWCloudScanEipPortInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eip', models.GenericIPAddressField(verbose_name='华为云EIP')),
                ('port', models.IntegerField(verbose_name='华为云EIP的暴露端口')),
                ('status', models.CharField(max_length=64, null=True, verbose_name='端口状态')),
                ('link_protocol', models.CharField(max_length=64, null=True, verbose_name='端口链接协议')),
                ('transport_protocol', models.CharField(max_length=64, null=True, verbose_name='端口传输协议')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
                ('region', models.CharField(max_length=32, verbose_name='华为云项目区域')),
                ('service_info', models.CharField(max_length=128, null=True, verbose_name='服务器版本信息')),
                ('protocol', models.IntegerField(verbose_name='协议:1_tcp/0_udp')),
            ],
            options={
                'verbose_name': '华为云高危端口扫描信息',
                'db_table': 'hw_cloud_scan_eip_port_info',
            },
        ),
        migrations.CreateModel(
            name='HWCloudScanEipPortStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
                ('status', models.IntegerField(verbose_name='操作状态')),
            ],
            options={
                'verbose_name': '华为云高危端口扫描状态表',
                'db_table': 'hw_cloud_scan_eip_port_status',
            },
        ),
        migrations.CreateModel(
            name='HWCloudScanObsAnonymousBucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
                ('bucket', models.CharField(max_length=128, verbose_name='华为云对象系统匿名桶')),
                ('url', models.CharField(max_length=256, null=True, verbose_name='华为云对象系统匿名桶的url')),
            ],
            options={
                'verbose_name': '华为云对象系统匿名桶',
                'db_table': 'hw_cloud_scan_obs_anonymous_bucket',
            },
        ),
        migrations.CreateModel(
            name='HWCloudScanObsAnonymousFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
                ('bucket', models.CharField(max_length=128, verbose_name='华为云对象系统匿名桶')),
                ('url', models.CharField(max_length=256, null=True, verbose_name='华为云对象系统匿名文件的url')),
                ('path', models.CharField(max_length=256, null=True, verbose_name='华为云对象系统匿名文件的path')),
                ('data', models.CharField(max_length=256, null=True, verbose_name='华为云对象系统匿名文件的敏感数据')),
            ],
            options={
                'verbose_name': '华为云对象系统匿名文件',
                'db_table': 'hw_cloud_scan_obs_anonymous_file',
            },
        ),
        migrations.CreateModel(
            name='HWCloudScanObsAnonymousStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
                ('status', models.IntegerField(verbose_name='操作状态')),
            ],
            options={
                'verbose_name': '华为云对象系统匿名桶状态表',
                'db_table': 'hw_cloud_scan_obs_anonymous_bucket_status',
            },
        ),
    ]