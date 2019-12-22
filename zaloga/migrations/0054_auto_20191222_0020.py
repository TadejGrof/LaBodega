# Generated by Django 2.2.5 on 2019-12-21 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0053_strosek_stroski_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='baza',
            name='prevoz',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='baza',
            name='tip',
            field=models.CharField(choices=[('inventura', 'Inventura'), ('prevzem', 'Prevzem'), ('odpis', 'Odpis'), ('vele_prodaja', 'Vele prodaja'), ('racun', 'Racun'), ('narocilo', 'Narocilo')], default='prevzem', max_length=20),
        ),
    ]
