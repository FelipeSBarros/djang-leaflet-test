# Generated by Django 3.1.7 on 2021-03-18 14:00

from django.db import migrations
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210318_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floraoccurrence',
            name='geom',
            field=djgeojson.fields.PointField(null=True),
        ),
    ]
