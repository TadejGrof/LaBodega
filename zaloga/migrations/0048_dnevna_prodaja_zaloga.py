# Generated by Django 2.2.5 on 2019-11-22 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0047_auto_20191122_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='dnevna_prodaja',
            name='zaloga',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Zaloga'),
        ),
    ]
