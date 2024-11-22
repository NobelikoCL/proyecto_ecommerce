# Generated by Django 5.1.3 on 2024-11-23 22:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_smart', '0003_remove_producto_proveedor_producto_activo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='padre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hijos', to='stock_smart.categoria'),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos', to='stock_smart.categoria'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos_marca', to='stock_smart.marca', verbose_name='Marca'),
        ),
    ]
