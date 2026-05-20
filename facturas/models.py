from django.db import models
from django.utils import timezone


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    # DecimalField to support half-stars (e.g. 4.5, 3.0)
    prioridad_estrellas = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=3.0
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return self.nombre


class Factura(models.Model):

    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('APROBADO',    'Aprobado'),
        ('CONFIRMADO',  'Confirmado'),
        ('PAGADO',      'Pagado'),
    ]

    TIPO_PAGO_CHOICES = [
        ('CONTADO',  'Contado'),
        ('CREDITO',  'Crédito'),
    ]

    id_factura = models.AutoField(primary_key=True)

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        db_column='proveedor_id'
    )

    folio = models.CharField(max_length=100, unique=True)

    tipo_pago = models.CharField(
        max_length=10,
        choices=TIPO_PAGO_CHOICES,
        default='CONTADO'
    )

    moneda = models.CharField(max_length=10, default='MXN')

    monto_original = models.DecimalField(max_digits=14, decimal_places=2)

    monto_mxn = models.DecimalField(max_digits=14, decimal_places=2)

    tipo_cambio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    # The invoice issue date — overdue days are calculated from this field
    fecha_factura = models.DateField(null=True, blank=True)

    # Partial payments: balance = total - total_abonado
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    total_abonado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    # Audit fields
    notas_auditoria = models.TextField(blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facturas'

    def __str__(self):
        return f"{self.folio} – {self.proveedor.nombre}"

    @property
    def saldo_neto(self):
        """Active balance pending payment."""
        return self.total - self.total_abonado

    @property
    def dias_vencidos(self):
        """Exact overdue days calculated dynamically vs today (May 20, 2026)."""
        if not self.fecha_factura:
            return 0
        TODAY = timezone.datetime(2026, 5, 20).date()
        delta = (TODAY - self.fecha_factura).days
        return max(delta, 0)

    def scoring(self):
        """
        Scoring 0-100:
          60% → supplier star rating (1–5 scale, supports decimals)
          40% → urgency: exact days / 120 (capped at 1.0)
        """
        estrellas = float(self.proveedor.prioridad_estrellas or 3)
        dias = self.dias_vencidos

        factor_proveedor = estrellas / 5.0
        factor_tiempo = min(dias / 120.0, 1.0) if dias > 0 else 0.0

        score = (factor_proveedor * 0.60) + (factor_tiempo * 0.40)
        return int(score * 100)