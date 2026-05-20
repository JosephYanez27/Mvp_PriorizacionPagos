from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Asegúrate de importar tu función 'leer_excel' desde el archivo donde la guardaste (ej: parser.py)
from cargas.services.excel_parser import leer_excel 

def vista_subir_excel(request):
    """Renderiza una vista simple para arrastrar o seleccionar el Excel (Opcional)"""
    return render(request, 'facturas/subir_excel.html')

@csrf_exempt  # Desactivamos csrf de forma temporal para facilitar la carga por Fetch API
def cargar_excel_api(request):
    """Recibe el archivo Excel del frontend y ejecuta el parser para poblar Neon"""
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        excel_recibido = request.FILES['archivo_excel']
        
        try:
            # Ejecutamos tu parser pasando directamente el archivo cargado en memoria
            total_procesado = leer_excel(excel_recibido)
            
            return JsonResponse({
                'success': True,
                'message': f'¡Base de datos poblada con éxito! Se procesaron {total_procesado} facturas individuales.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error crítico al procesar el archivo: {str(e)}'
            }, status=500)
            
    return JsonResponse({'success': False, 'message': 'Método no permitido o archivo faltante.'}, status=400)