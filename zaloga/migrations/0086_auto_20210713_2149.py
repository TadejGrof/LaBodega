# Generated by Django 2.2.16 on 2021-07-13 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zaloga', '0085_auto_20210706_1615'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sestavina',
            options={'ordering': ['dimenzija', 'tip']},
        ),
        migrations.AddField(
            model_name='dnevna_prodaja',
            name='tip',
            field=models.CharField(blank=True, default='Aktivno', max_length=20, null=True),
        ),
    ]
