# Generated by Django 5.1.3 on 2024-11-27 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_smart', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['name'], 'verbose_name': 'Marca', 'verbose_name_plural': 'Marcas'},
        ),
        migrations.AddField(
            model_name='brand',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nombre'),
        ),
    ]
