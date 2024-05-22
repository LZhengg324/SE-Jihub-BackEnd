# Generated by Django 5.0.3 on 2024-05-22 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('A', 'COMMIT'), ('B', 'ISSUE'), ('C', 'PR')], max_length=2)),
                ('remote_path', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('progress', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('A', 'COMPLETED'), ('B', 'INPROGRESS'), ('C', 'NOTSTART'), ('D', 'ILLEGAL')], max_length=2)),
                ('access', models.CharField(choices=[('A', 'NORMAL'), ('B', 'DISABLE')], default='A', max_length=2)),
                ('name', models.CharField(max_length=255)),
                ('outline', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('local_path', models.CharField(max_length=255)),
                ('remote_path', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_login_time', models.DateTimeField()),
                ('last_login_ip', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('color', models.CharField(choices=[('A', 'RED'), ('B', 'ORG'), ('C', 'GREEN'), ('D', 'BLUE'), ('E', 'PUR')], max_length=10)),
                ('status', models.CharField(choices=[('A', 'NORMAL'), ('B', 'ILLEGAL'), ('C', 'ADMIN'), ('D', 'ASSISTANT')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Pad',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('info', models.CharField(max_length=255)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='MyFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('outline', models.TextField()),
                ('type', models.CharField(choices=[('PRI', 'PRIVATE'), ('PUB', 'PUBLIC')], max_length=5)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectLinkPr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ghpr_id', models.IntegerField()),
                ('comment', models.TextField(default='No comment')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('repo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='ProgressTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.progress')),
                ('repo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo')),
            ],
        ),
        migrations.AddField(
            model_name='progress',
            name='repo_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo'),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(default='2050-12-31')),
                ('complete_time', models.DateTimeField(default='2050-12-31')),
                ('deadline', models.DateTimeField()),
                ('outline', models.TextField()),
                ('status', models.CharField(choices=[('A', 'COMPLETED'), ('B', 'INPROGRESS'), ('C', 'NOTSTART'), ('D', 'REVIEWING')], max_length=2)),
                ('contribute_level', models.IntegerField(default=0)),
                ('order', models.IntegerField(default=0)),
                ('link_pr', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.projectlinkpr')),
                ('parent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='manager_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user'),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('post_time', models.TimeField(auto_now_add=True)),
                ('post_type', models.CharField(choices=[('PROJ_ALL', 'PROJ_ALL'), ('PROJ_ONE', 'PROJ_ONE'), ('SYS_PROJ', 'SYS_PROJ'), ('SYS_ALL', 'SYS_ALL')], max_length=10)),
                ('is_received', models.BooleanField()),
                ('project_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('receiver_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to='myApp.user')),
                ('user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver_id', to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('deadline', models.DateTimeField()),
                ('content', models.TextField()),
                ('type', models.CharField(choices=[('A', 'NOTIFICATION'), ('B', 'ALARM')], default='B', max_length=5)),
                ('seen', models.BooleanField(default=False)),
                ('project_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('projectLinkPr_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.projectlinkpr')),
                ('belongingTask', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('C', 'CHECKED'), ('UC', 'UNCHECKED')], max_length=2)),
                ('type', models.CharField(choices=[('A', 'TEXT'), ('B', 'PIC'), ('C', 'FILE')], max_length=2)),
                ('content', models.CharField(max_length=255)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.group')),
                ('receive_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_user', to='myApp.user')),
                ('send_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receive_user', to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('outline', models.TextField()),
                ('content', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='CommentInPr',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('checkbox', models.BooleanField(default=False, null=True)),
                ('parent_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.commentinpr')),
                ('projectLinkPr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.projectlinkpr')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('repo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccessDoc',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserCollectDoc',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserDocLock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document', unique=True)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('A', 'NORMAL'), ('B', 'ADMIN')], max_length=2)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserPad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('A', 'OWNER'), ('B', 'GUEST')], max_length=2)),
                ('pad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.pad')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('A', 'NORMAL'), ('B', 'ADMIN'), ('C', 'DEVELOPER'), ('D', 'ASSISTANT'), ('E', 'ILLEGAL')], max_length=3)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserProjectRepo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('repo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='UserTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
    ]
