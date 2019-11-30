# Generated by Django 2.2.5 on 2019-09-23 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0016_vnos_skupna_cena'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventura_vnos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yellow', models.IntegerField(blank=True, default=None, null=True)),
                ('white', models.IntegerField(blank=True, default=None, null=True)),
                ('inventura', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Inventura')),
                ('sestavina', models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Sestavina')),
            ],
        ),
    ]
