# Generated by Django 3.2.6 on 2021-08-22 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('residences', '0001_initial'),
        ('corporations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporation',
            name='cities',
            field=models.ManyToManyField(related_name='corporations', to='residences.City'),
        ),
    ]
