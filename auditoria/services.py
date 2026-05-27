from facturas.models import Factura


def obtener_facturas_proveedor(proveedor_id):

    facturas = Factura.objects.filter(
        proveedor_id=proveedor_id,
        estado='PENDIENTE'
    )

    resultado = []

    for f in facturas:

        resultado.append({
            "id": f.id_factura,
            "folio": f.folio,
            "saldo_neto": float(f.saldo_neto),
            "dias_vencidos": f.dias_vencidos,
            "moneda": f.moneda
        })

    return resultado

def autorizar_facturas_multiple(facturas_data):

    for item in facturas_data:

        factura = Factura.objects.get(
            id=item['id']
        )

        factura.total_abonado = item['abono']

        factura.estado = 'APROBADO'

        factura.save()

    return True