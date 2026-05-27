import json
import os
import tempfile

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from auditoria.services import (
    autorizar_facturas_multiple,
    obtener_facturas_proveedor
)

from cargas.services.excel_parser import leer_excel
from cargas.services.save_service import guardar_facturas


def pantalla_upload(request):

    return render(
        request,
        'upload.html'
    )


@csrf_exempt
def subir_excel(request):

    if request.method != 'POST':

        return JsonResponse({
            'error': 'Método no permitido'
        }, status=405)

    archivo = request.FILES.get('archivo')

    if not archivo:

        return JsonResponse({
            'error': 'No se recibió archivo'
        }, status=400)

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.xlsx'
    )

    for chunk in archivo.chunks():
        temp.write(chunk)

    temp.close()

    try:

        facturas = leer_excel(temp.name)

        total = guardar_facturas(facturas)

        return JsonResponse({

            'success': True,
            'facturas_guardadas': total

        })

    except Exception as e:

        return JsonResponse({

            'success': False,
            'error': str(e)

        }, status=500)

    finally:

        os.unlink(temp.name)


def facturas_proveedor(request, proveedor_id):

    try:

        data = obtener_facturas_proveedor(
            proveedor_id
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "ok": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
def autorizar_multiple(request):

    try:

        body = json.loads(request.body)

        facturas = body.get(
            'facturas',
            []
        )

        autorizar_facturas_multiple(
            facturas
        )

        return JsonResponse({
            "ok": True
        })

    except Exception as e:

        return JsonResponse({
            "ok": False,
            "error": str(e)
        }, status=500)