# Generated by Django 5.2.3 on 2025-07-09 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0006_alter_application_score_alter_interaction_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
    ]
