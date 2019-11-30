# Generated by Django 2.2.5 on 2019-10-29 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0024_auto_20191029_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kontejner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stevilka', models.CharField(default='', max_length=20)),
                ('posiljatelj', models.CharField(default='', max_length=20)),
                ('drzava', models.CharField(default='', max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='prevzem',
            name='kontejner',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Kontejner'),
        ),
    ]
