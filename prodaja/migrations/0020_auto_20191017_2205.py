# Generated by Django 2.2.5 on 2019-10-17 20:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('prodaja', '0019_auto_20191017_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dnevna_prodaja',
            name='datum',
            field=models.DateField(default=datetime.datetime(2019, 10, 17, 20, 5, 15, 237832, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='vele_prodaja',
            name='datum',
            field=models.DateField(default=datetime.datetime(2019, 10, 17, 20, 5, 15, 406967, tzinfo=utc)),
        ),
    ]
