# Generated by Django 5.0.2 on 2024-02-12 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0021_show_badge_info_and_progress'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='courseclass',
            options={'ordering': ['-end_date', 'code'], 'verbose_name_plural': 'Classes'},
        ),
    ]
