from facturas.models import Factura, Proveedor


def guardar_facturas(lista_facturas):

    total_guardadas = 0

    for data in lista_facturas:

        proveedor_nombre = data.get('proveedor')

        if not proveedor_nombre:
            continue

        proveedor, _ = Proveedor.objects.get_or_create(
            nombre=proveedor_nombre
        )

        Factura.objects.create(

            proveedor=proveedor,

            folio=data.get('folio'),

            moneda=data.get('moneda'),

            monto_original=data.get('monto_original'),

            monto_mxn=data.get('monto_mxn'),

            tipo_cambio=data.get('tipo_cambio'),

            fecha_factura=data.get('fecha_factura'),

            dias_vencidos=data.get('dias_vencidos'),

            total=data.get('total')
        )

        total_guardadas += 1

    return total_guardadas