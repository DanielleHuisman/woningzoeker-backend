# Generated by Django 3.2.6 on 2021-08-27 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationprovider',
            name='identifier',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]