# Generated by Django 4.2.11 on 2024-05-17 11:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('educvideos', '0011_alter_videomaterials_file_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
