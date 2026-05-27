
from django.urls import path

from .views import *
from api.views import autorizar_multiple, facturas_proveedor

from auditoria import views


urlpatterns = [

    path(
        'proveedor/<int:proveedor_id>/',
        views.auditar_proveedor,
        name='auditar_proveedor'
    ),

    path(
        'facturas/autorizar-multiple/',
        autorizar_multiple
    ),
]