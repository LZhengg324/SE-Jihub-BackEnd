# Generated by Django 5.0.3 on 2024-04-23 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0003_remove_pullrequest_creator_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='link_pr',
        ),
        migrations.AddField(
            model_name='projectlinkpr',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projectlinkpr',
            name='ghpr_id',
            field=models.IntegerField(unique=True),
        ),
    ]
