# Generated by Django 2.2.5 on 2019-09-12 18:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0007_auto_20190912_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vnos',
            name='inventura',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Inventura'),
        ),
        migrations.CreateModel(
            name='Odpis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=15)),
                ('datum', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='aktivno', max_length=10)),
                ('zaloga', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Zaloga')),
            ],
        ),
        migrations.AddField(
            model_name='vnos',
            name='odpis',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Odpis'),
        ),
    ]
