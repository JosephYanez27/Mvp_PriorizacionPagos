from django.urls import path

from .views import (
    subir_excel,
    pantalla_upload
)


urlpatterns = [
    path(
        '',
        pantalla_upload
    ),

    path(
        'cargas/excel/',
        subir_excel
    )
]