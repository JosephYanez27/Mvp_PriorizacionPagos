from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Proveedor, Factura

class FacturasViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.proveedor = Proveedor.objects.create(nombre="Proveedor Test", prioridad_estrellas=4.5)
        self.factura1 = Factura.objects.create(
            proveedor=self.proveedor,
            folio="FOLIO-001",
            tipo_pago="CONTADO",
            moneda="MXN",
            monto_original=Decimal("1000.00"),
            monto_mxn=Decimal("1000.00"),
            tipo_cambio=Decimal("1.0"),
            total=Decimal("1000.00"),
            total_abonado=Decimal("0.00"),
            estado="PENDIENTE"
        )
        self.factura2 = Factura.objects.create(
            proveedor=self.proveedor,
            folio="FOLIO-002",
            tipo_pago="CREDITO",
            moneda="USD",
            monto_original=Decimal("100.00"),
            monto_mxn=Decimal("2000.00"),
            tipo_cambio=Decimal("20.0"),
            total=Decimal("2000.00"),
            total_abonado=Decimal("500.00"), # saldo_neto = 1500
            estado="PENDIENTE"
        )

    def test_api_facturas_por_proveedor(self):
        url = f"/api/proveedores/{self.proveedor.id_proveedor}/facturas/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        # Should be ordered by scoring DESC
        self.assertTrue(data[0]["scoring"] >= data[1]["scoring"])

    def test_api_autorizar_lote(self):
        url = "/api/facturas/autorizar-lote/"
        payload = {
            "autorizaciones": [
                {
                    "id_factura": self.factura1.id_factura,
                    "abono": 1000.00,
                    "notas_auditoria": "Abono completo"
                },
                {
                    "id_factura": self.factura2.id_factura,
                    "abono": 500.00,
                    "notas_auditoria": "Abono parcial"
                }
            ]
        }
        response = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        
        # Verify db changes
        f1 = Factura.objects.get(pk=self.factura1.id_factura)
        self.assertEqual(f1.estado, "APROBADO")
        self.assertEqual(f1.total_abonado, Decimal("1000.00"))
        self.assertEqual(f1.notas_auditoria, "Abono completo")

        f2 = Factura.objects.get(pk=self.factura2.id_factura)
        self.assertEqual(f2.estado, "APROBADO")
        self.assertEqual(f2.total_abonado, Decimal("1000.00")) # 500 original + 500 abono
        self.assertEqual(f2.notas_auditoria, "Abono parcial")

    def test_api_autorizar_lote_exceeds_balance(self):
        url = "/api/facturas/autorizar-lote/"
        payload = {
            "autorizaciones": [
                {
                    "id_factura": self.factura2.id_factura,
                    "abono": 2000.00, # Exceeds saldo_neto of 1500
                    "notas_auditoria": "Invalid"
                }
            ]
        }
        response = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertIn("supera el saldo neto", data["error"])

        # DB should not be updated (atomic transaction)
        f2 = Factura.objects.get(pk=self.factura2.id_factura)
        self.assertEqual(f2.estado, "PENDIENTE")
        self.assertEqual(f2.total_abonado, Decimal("500.00"))
