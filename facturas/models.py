from django.db import models

# Create your models here.
moneda = models.CharField(
    max_length=10,
    default='MXN'
)

monto_original = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    default=0
)

tipo_cambio = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    default=1
)

monto_mxn = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    default=0
)