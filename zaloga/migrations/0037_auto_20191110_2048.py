# Generated by Django 2.2.5 on 2019-11-10 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0036_auto_20191110_2043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vnos',
            name='sprememba',
        ),
        migrations.DeleteModel(
            name='Sprememba',
        ),
    ]
