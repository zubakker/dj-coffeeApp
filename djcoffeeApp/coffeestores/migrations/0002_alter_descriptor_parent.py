# Generated by Django 4.2.4 on 2023-08-21 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coffeestores', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='descriptor',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='coffeestores.descriptor'),
        ),
    ]
