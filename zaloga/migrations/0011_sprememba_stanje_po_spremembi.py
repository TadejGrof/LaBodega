# Generated by Django 2.2.5 on 2019-09-15 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0010_auto_20190915_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprememba',
            name='stanje_po_spremembi',
            field=models.IntegerField(default=0),
        ),
    ]
