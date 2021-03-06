# Generated by Django 3.1.7 on 2021-04-25 00:03

from django.db import migrations, models
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210318_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fenomenos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Fenomeno mapeado')),
                ('data', models.DateField(verbose_name='Data da observação')),
                ('hora', models.TimeField()),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('geom', djgeojson.fields.PointField()),
            ],
        ),
        migrations.DeleteModel(
            name='FloraOccurrence',
        ),
    ]
