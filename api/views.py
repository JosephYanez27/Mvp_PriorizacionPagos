from sys import path

from django.shortcuts import render

# Create your views here.
import os
import tempfile

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from cargas.services.excel_parser import leer_excel
from cargas.services.save_service import guardar_facturas
def pantalla_upload(request):


    path(
        'cargas/excel/',
        subir_excel
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

    # -----------------------------------------
    # GUARDAR TEMPORAL
    # -----------------------------------------

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