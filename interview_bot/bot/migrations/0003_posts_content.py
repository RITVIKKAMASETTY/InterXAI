# Generated by Django 5.1.4 on 2024-12-22 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]