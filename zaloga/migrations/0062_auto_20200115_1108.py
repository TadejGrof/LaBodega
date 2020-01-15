# Generated by Django 2.2.5 on 2020-01-15 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prodaja', '0049_remove_stranka_stevilo'),
        ('zaloga', '0061_zaposleni'),
    ]

    operations = [
        migrations.AddField(
            model_name='zaposleni',
            name='naslov',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='prodaja.Naslov'),
        ),
        migrations.AlterField(
            model_name='zaposleni',
            name='ime',
            field=models.CharField(default='/', max_length=20),
        ),
        migrations.AlterField(
            model_name='zaposleni',
            name='priimek',
            field=models.CharField(default='/', max_length=20),
        ),
    ]
