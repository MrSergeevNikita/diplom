# Generated by Django 4.2.11 on 2024-05-20 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educvideos', '0024_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('done', 'Done'), ('denied', 'Denied')], default='Pending', max_length=10),
        ),
    ]