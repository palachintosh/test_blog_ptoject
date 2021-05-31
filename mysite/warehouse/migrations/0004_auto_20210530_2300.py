# Generated by Django 2.2.5 on 2021-05-30 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_warehouses_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouses',
            name='products',
        ),
        migrations.AddField(
            model_name='product',
            name='warehouse_products',
            field=models.ManyToManyField(blank=True, related_name='related_products', to='warehouse.Warehouses'),
        ),
    ]
