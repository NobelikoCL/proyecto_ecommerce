# Generated by Django 5.1.3 on 2024-11-24 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_smart', '0006_remove_configuracionhome_max_productos_por_seccion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='precio_oferta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
