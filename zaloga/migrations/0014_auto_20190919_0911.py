# Generated by Django 2.2.5 on 2019-09-19 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0013_auto_20190917_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='sestavina',
            name='dnevna_prodaja_white',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='sestavina',
            name='dnevna_prodaja_yellow',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='sestavina',
            name='vele_prodaja_white',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='sestavina',
            name='vele_prodaja_yellow',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
    ]
