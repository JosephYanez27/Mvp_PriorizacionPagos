from django.urls import path

from cargas.views import vista_subida

urlpatterns = [
    path(
        'subir/',
        vista_subida,
        name='subir_excel_html'
    )
]