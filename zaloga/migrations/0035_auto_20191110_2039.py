# Generated by Django 2.2.5 on 2019-11-10 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zaloga', '0034_auto_20191106_2116'),
    ]

    operations = [
        migrations.CreateModel(
            name='Baza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=15)),
                ('datum', models.DateField(default=django.utils.timezone.now)),
                ('sprememba_zaloge', models.IntegerField(default=-1)),
                ('tip', models.CharField(choices=[('inventura', 'Inventura'), ('prevzem', 'Prevzem'), ('odpis', 'Odpis'), ('vele_prodaja', 'Vele prodaja'), ('racun', 'Racun'), ('dnevna_prodaja', 'Dnevna prodjaja')], default='prevzem', max_length=20)),
                ('status', models.CharField(default='aktivno', max_length=10)),
                ('author', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('kontejner', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Kontejner')),
            ],
        ),
        migrations.RemoveField(
            model_name='inventura_vnos',
            name='inventura',
        ),
        migrations.RemoveField(
            model_name='inventura_vnos',
            name='sestavina',
        ),
        migrations.RemoveField(
            model_name='odpis',
            name='author',
        ),
        migrations.RemoveField(
            model_name='odpis',
            name='zaloga',
        ),
        migrations.RemoveField(
            model_name='prevzem',
            name='author',
        ),
        migrations.RemoveField(
            model_name='prevzem',
            name='kontejner',
        ),
        migrations.RemoveField(
            model_name='prevzem',
            name='zaloga',
        ),
        migrations.RemoveField(
            model_name='sprememba',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='sprememba',
            name='datum_spremembe',
        ),
        migrations.RemoveField(
            model_name='sprememba',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='sprememba',
            name='sprememba_zaloge',
        ),
        migrations.RemoveField(
            model_name='sprememba',
            name='tip_spremembe',
        ),
        migrations.RemoveField(
            model_name='vnos',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='vnos',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='zaloga',
            name='title',
            field=models.CharField(default='skladisce', max_length=20),
        ),
        migrations.DeleteModel(
            name='Inventura',
        ),
        migrations.DeleteModel(
            name='Inventura_vnos',
        ),
        migrations.DeleteModel(
            name='Odpis',
        ),
        migrations.DeleteModel(
            name='Prevzem',
        ),
        migrations.AddField(
            model_name='baza',
            name='zaloga',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Zaloga'),
        ),
        migrations.AddField(
            model_name='sprememba',
            name='baza',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Baza'),
        ),
        migrations.AddField(
            model_name='vnos',
            name='baza',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='zaloga.Baza'),
        ),
    ]
