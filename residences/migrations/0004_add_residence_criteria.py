# Generated by Django 3.2.7 on 2021-09-18 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('residences', '0003_fix_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='residence',
            name='assignment',
            field=models.CharField(choices=[('HOUSE_DETACHED', 'House Detached'), ('HOUSE_SEMI_DETACHED', 'House Semi Detached'), ('HOUSE_DUPLEX', 'House Duplex'), ('HOUSE_TERRACED', 'House Terraced'), ('HOUSE_UNKNOWN', 'House Unknown'), ('APARTMENT', 'Apartment'), ('MAISONNETTE', 'Maisonnette'), ('UNKNOWN', 'Unknown')], default='DRAW', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='residence',
            name='max_age',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='residence',
            name='max_children',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='residence',
            name='max_residents',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='residence',
            name='min_age',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='residence',
            name='min_children',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='residence',
            name='min_residents',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='residence',
            name='type',
            field=models.CharField(choices=[('DRAW', 'Draw'), ('REGISTRATION_TIME', 'Registration Time')], max_length=255),
        ),
    ]