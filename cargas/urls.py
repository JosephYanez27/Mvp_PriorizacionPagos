from django.urls import path
from . import views  # Asegúrate de que apunte a donde tienes tu vista 'cargar_excel_api'

urlpatterns = [
    # Al estar incluido dentro de 'cargas/', la URL final para el navegador será: /cargas/excel/
    path('excel/', views.cargar_excel_api, name='cargar_excel_api'),
]