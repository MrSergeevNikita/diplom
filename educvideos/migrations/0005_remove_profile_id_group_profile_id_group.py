# Generated by Django 4.2.11 on 2024-04-30 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educvideos', '0004_profile_patronymic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='id_group',
        ),
        migrations.AddField(
            model_name='profile',
            name='id_group',
            field=models.ManyToManyField(blank=True, null=True, to='educvideos.group'),
        ),
    ]