# Generated by Django 3.2.25 on 2024-04-23 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('outline', models.TextField()),
                ('content', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('outline', models.TextField()),
                ('type', models.CharField(choices=[('PRI', 'PRIVATE'), ('PUB', 'PUBLIC')], max_length=5)),
            ],
        ),
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
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('start_time', models.DateTimeField(default='2050-12-31')),
                ('complete_time', models.DateTimeField(default='2050-12-31')),
                ('deadline', models.DateTimeField()),
                ('outline', models.TextField()),
                ('status', models.CharField(choices=[('A', 'COMPLETED'), ('B', 'INPROGRESS'), ('C', 'NOTSTART'), ('D', 'REVIEWING')], max_length=2)),
                ('contribute_level', models.IntegerField(default=0)),
                ('order', models.IntegerField(default=0)),
                ('parent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
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
                ('color', models.CharField(choices=[('A', 'RED'), ('B', 'ORG'), ('C', 'GREEN'), ('D', 'BLUE'), ('E', 'PUR')], max_length=10)),
                ('status', models.CharField(choices=[('A', 'NORMAL'), ('B', 'ILLEGAL'), ('C', 'ADMIN'), ('D', 'ASSISTANT')], max_length=2)),
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
            name='UserProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('A', 'NORMAL'), ('B', 'ADMIN'), ('C', 'DEVELOPER')], max_length=3)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
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
            name='UserDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document')),
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
            name='UserCollectDoc',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.document')),
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
            name='PullRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('A', 'OPEN'), ('B', 'MERGED'), ('C', 'CLOSED')], max_length=2)),
                ('creator_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='manager_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user'),
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
            name='PrLinkTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pr_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.pullrequest')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
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
                ('belongingTask', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.task')),
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
        migrations.AddField(
            model_name='group',
            name='project_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project'),
        ),
        migrations.AddField(
            model_name='document',
            name='project_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project'),
        ),
        migrations.AddField(
            model_name='document',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user'),
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
    ]
