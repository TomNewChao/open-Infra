# Generated by Django 3.2.18 on 2023-03-16 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HWCloudAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户name')),
                ('ak', models.CharField(max_length=255, verbose_name='华为云账户的ak')),
                ('sk', models.CharField(max_length=255, verbose_name='华为云账户的sk')),
            ],
            options={
                'verbose_name': '华为云账户',
                'db_table': 'hw_cloud_account',
            },
        ),
        migrations.CreateModel(
            name='HWCloudEipInfo',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False, verbose_name='华为云eip的id')),
                ('eip', models.GenericIPAddressField()),
                ('eip_status', models.IntegerField(null=True, verbose_name='华为云eip的status')),
                ('eip_type', models.IntegerField(null=True, verbose_name='华为云eip的type')),
                ('eip_zone', models.CharField(max_length=64, null=True, verbose_name='华为云eip归属区域')),
                ('bandwidth_id', models.CharField(max_length=64, null=True, verbose_name='华为云的带宽id')),
                ('bandwidth_name', models.CharField(max_length=64, null=True, verbose_name='华为云的带宽name')),
                ('bandwidth_size', models.IntegerField(null=True, verbose_name='华为云的带宽size')),
                ('example_id', models.CharField(max_length=64, null=True, verbose_name='实例id')),
                ('example_name', models.CharField(max_length=64, null=True, verbose_name='实例name')),
                ('example_type', models.CharField(max_length=32, null=True, verbose_name='实例type')),
                ('create_time', models.DateTimeField(verbose_name='创建时间')),
                ('refresh_time', models.DateTimeField(verbose_name='刷新时间')),
                ('account', models.CharField(max_length=32, verbose_name='华为云账户名称')),
            ],
            options={
                'verbose_name': '华为云eip信息',
                'db_table': 'hw_cloud_eip_info',
            },
        ),
        migrations.CreateModel(
            name='ServiceInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=64, null=True, verbose_name='服务名称')),
                ('namespace', models.CharField(max_length=64, null=True, verbose_name='命名空间')),
                ('cluster', models.CharField(max_length=64, null=True, verbose_name='集群名称')),
                ('region', models.CharField(max_length=64, null=True, verbose_name='区域')),
            ],
            options={
                'verbose_name': '服务信息表',
                'verbose_name_plural': '服务信息表',
                'db_table': 'service_info',
            },
        ),
        migrations.CreateModel(
            name='ServiceSlaConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=64, null=True, verbose_name='服务域名')),
                ('service_alias', models.CharField(max_length=64, null=True, verbose_name='服务别名')),
                ('service_introduce', models.CharField(max_length=64, null=True, verbose_name='服务介绍')),
            ],
            options={
                'verbose_name': '服务SLA_CONFIG表',
                'verbose_name_plural': '服务SLA_CONFIG表',
                'db_table': 'service_sla_config',
            },
        ),
        migrations.CreateModel(
            name='ServiceSla',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=64, null=True, verbose_name='服务域名')),
                ('service_alias', models.CharField(max_length=64, null=True, verbose_name='服务别名')),
                ('service_introduce', models.CharField(max_length=64, null=True, verbose_name='服务介绍')),
                ('service_zone', models.CharField(max_length=64, null=True, verbose_name='服务归属社区')),
                ('month_abnormal_time', models.FloatField(null=True, verbose_name='月度异常累计时间')),
                ('year_abnormal_time', models.FloatField(null=True, verbose_name='年度异常累计时间')),
                ('month_sla', models.FloatField(null=True, verbose_name='月度sla')),
                ('year_sla', models.FloatField(null=True, verbose_name='年度sla')),
                ('remain_time', models.FloatField(null=True, verbose_name='年度剩余sla配额')),
                ('service', models.ForeignKey(default='', on_delete=django.db.models.deletion.SET_DEFAULT, to='app_resources.serviceinfo')),
            ],
            options={
                'verbose_name': '服务SLA表',
                'verbose_name_plural': '服务SLA表',
                'db_table': 'service_sla',
            },
        ),
        migrations.CreateModel(
            name='ServiceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(max_length=128, null=True, verbose_name='镜像路径')),
                ('repository', models.CharField(max_length=128, null=True, verbose_name='仓库')),
                ('branch', models.CharField(max_length=64, null=True, verbose_name='分支')),
                ('developer', models.CharField(max_length=64, null=True, verbose_name='开发者')),
                ('email', models.EmailField(max_length=254, null=True)),
                ('base_image', models.CharField(max_length=128, null=True, verbose_name='基础构建镜像')),
                ('base_os', models.CharField(max_length=128, null=True, verbose_name='基础操作系统')),
                ('pipline_url', models.CharField(max_length=256, null=True, verbose_name='流水线url')),
                ('num_download', models.IntegerField(null=True, verbose_name='下载次数')),
                ('size', models.CharField(max_length=32, null=True, verbose_name='镜像大小')),
                ('cpu_limit', models.CharField(max_length=64, null=True, verbose_name='cpu限制')),
                ('mem_limit', models.CharField(max_length=64, null=True, verbose_name='内存限制')),
                ('service', models.ForeignKey(default='', on_delete=django.db.models.deletion.SET_DEFAULT, to='app_resources.serviceinfo')),
            ],
            options={
                'verbose_name': '服务镜像表',
                'verbose_name_plural': '服务镜像表',
                'db_table': 'service_image',
            },
        ),
        migrations.CreateModel(
            name='HWCloudProjectInfo',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False, verbose_name='华为云项目id')),
                ('zone', models.CharField(max_length=32, verbose_name='华为云项目zone')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_resources.hwcloudaccount', verbose_name='外键，关联华为云的账户id')),
            ],
            options={
                'verbose_name': '华为云项目信息',
                'db_table': 'hw_cloud_project_info',
            },
        ),
    ]