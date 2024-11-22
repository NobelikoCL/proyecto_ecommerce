# Generated by Django 5.1.3 on 2024-11-23 22:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_smart', '0002_marca_producto_marca'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='proveedor',
        ),
        migrations.AddField(
            model_name='producto',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos', to='stock_smart.marca', verbose_name='Marca'),
        ),
    ]
