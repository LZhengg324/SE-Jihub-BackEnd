# Generated by Django 5.0.3 on 2024-04-23 07:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_alter_task_status_alter_user_status_branch_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pullrequest',
            name='creator_id',
        ),
        migrations.RemoveField(
            model_name='pullrequest',
            name='project_id',
        ),
        migrations.CreateModel(
            name='ProjectLinkPr',
            fields=[
                ('ghpr_id', models.IntegerField(default=-1, primary_key=True, serialize=False)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.project')),
                ('repo_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.repo')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.user')),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='link_pr',
            field=models.ForeignKey(blank=True, default=-1, null=True, on_delete=django.db.models.deletion.CASCADE, to='myApp.projectlinkpr'),
        ),
        migrations.DeleteModel(
            name='PrLinkTask',
        ),
        migrations.DeleteModel(
            name='PullRequest',
        ),
    ]
