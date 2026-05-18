from facturas.models import Factura, Proveedor

from datetime import datetime


def guardar_facturas(lista_facturas):

    creadas = 0

    for item in lista_facturas:

        proveedor_obj, _ = Proveedor.objects.get_or_create(
            nombre=item['proveedor'],
            defaults={
                'prioridad_estrellas': 3
            }
        )

        fecha = None

        try:

            if item['fecha_factura']:

                fecha = datetime.strptime(
                    str(item['fecha_factura']),
                    "%d/%m/%Y"
                ).date()

        except:
            fecha = None

        Factura.objects.create(

            proveedor=proveedor_obj,

            folio=item['folio'],

            moneda=item['moneda'],

            monto_original=item['monto_original'],

            monto_mxn=item['monto_mxn'],

            tipo_cambio=item['tipo_cambio'],

            fecha_factura=fecha,

            dias_vencidos=item['dias_vencidos'],

            total=item['total'],

            estado='PENDIENTE'
        )

        creadas += 1

    return creadas