# Generated by Django 2.2.16 on 2021-07-06 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0079_auto_20210706_1315'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vnoszaloge',
            options={'ordering': ['zaloga', 'sestavina']},
        ),
    ]
