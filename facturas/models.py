from django.db import models


class Proveedor(models.Model):

    id_proveedor = models.AutoField(primary_key=True)

    nombre = models.CharField(max_length=255)

    prioridad_estrellas = models.IntegerField(default=3)

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return self.nombre


class Factura(models.Model):

    id_factura = models.AutoField(primary_key=True)

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        db_column='proveedor_id'
    )

    folio = models.CharField(max_length=100)

    moneda = models.CharField(
        max_length=10,
        default='MXN'
    )

    monto_original = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    monto_mxn = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    tipo_cambio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    fecha_factura = models.DateField(
        null=True,
        blank=True
    )

    dias_vencidos = models.IntegerField(default=0)

    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=30,
        default='PENDIENTE'
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'facturas'