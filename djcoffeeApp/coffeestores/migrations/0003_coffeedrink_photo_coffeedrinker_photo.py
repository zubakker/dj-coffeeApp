# Generated by Django 4.2.4 on 2023-08-23 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coffeestores', '0002_alter_descriptor_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='coffeedrink',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='files'),
        ),
        migrations.AddField(
            model_name='coffeedrinker',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='files'),
        ),
    ]
