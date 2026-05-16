import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0001_initial'),
        ('terceros', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_compra', models.DateField(auto_now_add=True)),
                ('total_compra', models.DecimalField(decimal_places=2, max_digits=12)),
                ('estado', models.CharField(
                    choices=[
                        ('pendiente', 'Pendiente'),
                        ('recibida', 'Recibida'),
                        ('anulada', 'Anulada'),
                    ],
                    default='recibida',
                    max_length=20,
                )),
                ('nota', models.TextField(blank=True, null=True)),
                ('proveedor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='compras_proveedor',
                    to='terceros.proveedor',
                )),
            ],
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('compra', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='detalles_compra',
                    related_query_name='detalle_compra',
                    to='compras.compra',
                )),
                ('producto', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='detalles_compra_producto',
                    related_query_name='detalle_compra_producto',
                    to='productos.producto',
                )),
            ],
        ),
    ]
