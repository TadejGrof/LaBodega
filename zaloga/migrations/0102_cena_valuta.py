# Generated by Django 2.2.16 on 2021-08-01 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0012_valuta'),
        ('zaloga', '0101_auto_20210801_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='cena',
            name='valuta',
            field=models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.Valuta'),
        ),
    ]
