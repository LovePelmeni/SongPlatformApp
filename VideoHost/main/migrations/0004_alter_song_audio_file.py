# Generated by Django 4.0.4 on 2022-06-07 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_blocklist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='audio_file',
            field=models.CharField(max_length=300, null=True, verbose_name='AWS Audio File Link'),
        ),
    ]
