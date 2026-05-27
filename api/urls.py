from django.urls import path

from .views import (
    pantalla_upload,
    subir_excel,
    facturas_proveedor,
    autorizar_multiple
)

urlpatterns = [

    path(
        '',
        pantalla_upload
    ),

    path(
        'cargas/excel/',
        subir_excel
    ),

    path(
        'proveedor/<int:proveedor_id>/',
        facturas_proveedor
    ),

    path(
        'autorizar/',
        autorizar_multiple
    )

]