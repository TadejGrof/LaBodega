# Generated by Django 2.2.5 on 2019-09-19 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prodaja', '0007_auto_20190919_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stranka',
            name='mail',
            field=models.CharField(default='', max_length=40),
        ),
    ]
