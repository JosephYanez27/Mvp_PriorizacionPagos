# from django.shortcuts import render
# from django.http import HttpResponse, JsonResponse
# from .services import obtener_priorizacion_pagos


# def index(request):
#     """Vista principal: renderiza el dashboard HTML"""
#     return render(request, 'dashboard/dashboard.html')


# def vista_dashboard_pagos(request):
#     """
#     Vista API que retorna el scoring de priorización de pagos en JSON.
#     Agrupa facturas pendientes por proveedor y calcula su prioridad.
#     """
#     try:
#         # Ejecutamos el servicio de priorización
#         datos_para_pantalla = obtener_priorizacion_pagos()
        
#         # Retornamos el JSON estructurado
#         return JsonResponse(datos_para_pantalla, safe=False)
        
#     except Exception as e:
#         return JsonResponse({
#             "estatus": "error",
#             "mensaje": str(e)
#         }, status=500)
        
        
from django.shortcuts import render


def priorizacion(request):
    return render(request, 'tesoreria/priorizacion.html')


def confirmacion(request):
    return render(request, 'tesoreria/confirmacion.html')


def conciliacion(request):
    return render(request, 'tesoreria/conciliacion.html')


def auditoria(request):
    return render(request, 'tesoreria/auditoria.html')