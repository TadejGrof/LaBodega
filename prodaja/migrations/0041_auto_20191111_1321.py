# Generated by Django 2.2.5 on 2019-11-11 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prodaja', '0040_auto_20191111_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vele_prodaja',
            name='author',
        ),
        migrations.RemoveField(
            model_name='vele_prodaja',
            name='prodaja',
        ),
        migrations.RemoveField(
            model_name='vele_prodaja',
            name='stranka',
        ),
        migrations.DeleteModel(
            name='Racun',
        ),
        migrations.DeleteModel(
            name='Vele_prodaja',
        ),
    ]
