import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('terceros', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('uuid_public', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre_producto', models.CharField(max_length=80)),
                ('fecha_vencimiento', models.DateField()),
                ('codigo_barras', models.BigIntegerField(db_index=True, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=12)),
                ('stock', models.IntegerField(default=0)),
                ('proveedor', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='productos_proveedor',
                    related_query_name='producto_proveedor',
                    to='terceros.proveedor',
                )),
            ],
        ),
    ]
