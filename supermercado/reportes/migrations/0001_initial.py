import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id_reporte', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_index=True, max_length=150)),
                ('tipo', models.CharField(
                    choices=[
                        ('ventas', 'Ventas'),
                        ('compras', 'Compras'),
                        ('productos', 'Productos'),
                        ('clientes', 'Clientes'),
                        ('proveedores', 'Proveedores'),
                        ('stock_critico', 'Stock crítico'),
                        ('rentabilidad', 'Rentabilidad por producto'),
                    ],
                    db_index=True,
                    default='ventas',
                    max_length=20,
                )),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateField(auto_now_add=True)),
                ('usuario_creacion', models.CharField(default='admin', max_length=60)),
                ('activo_tf', models.BooleanField(default=True)),
                ('columnas_seleccionadas', models.JSONField(default=list)),
                ('filtros', models.JSONField(default=dict)),
                ('agrupacion', models.CharField(blank=True, max_length=60, null=True)),
                ('orden', models.CharField(blank=True, max_length=60, null=True)),
                ('limite', models.PositiveIntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('reportes', models.ManyToManyField(blank=True, related_name='categorias', to='reportes.reporte')),
            ],
        ),
    ]
