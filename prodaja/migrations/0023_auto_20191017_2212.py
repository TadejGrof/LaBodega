# Generated by Django 2.2.5 on 2019-10-17 20:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0022_auto_20191016_1622'),
        ('prodaja', '0022_auto_20191017_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='prodaja',
            name='zaloga',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Zaloga'),
        ),
        migrations.AlterField(
            model_name='dnevna_prodaja',
            name='datum',
            field=models.DateField(default=datetime.datetime(2019, 10, 17, 20, 12, 0, 632502, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='vele_prodaja',
            name='datum',
            field=models.DateField(default=datetime.datetime(2019, 10, 17, 20, 12, 0, 767447, tzinfo=utc)),
        ),
    ]
