"""
urls.py — Wire up all Treasury API endpoints.
Include this in your project's main urls.py:
    path('', include('facturas.urls')),
"""

from django.urls import path
from . import views

urlpatterns = [
    # Screen 1 — Prioritization
    path("api/pagos/",                              views.api_pendientes,          name="api_pendientes"),
    path('api/pagos/por-proveedor/', views.api_pendientes_por_proveedor),
    path("api/facturas/<int:id_factura>/autorizar/", views.api_autorizar,           name="api_autorizar"),
    path("api/facturas/<int:id_factura>/revertir/",  views.api_revertir_a_pendiente, name="api_revertir"),

    # Screen 2 — Tab A: Confirmation Tray
    path("api/aprobados/",                          views.api_aprobados,           name="api_aprobados"),
    path("api/facturas/<int:id_factura>/confirmar/", views.api_confirmar,           name="api_confirmar"),

    # Screen 2 — Tab B: Export & Reconciliation
    path("api/confirmados/",                        views.api_confirmados,         name="api_confirmados"),
    path("api/exportar-remesa/",                    views.api_exportar_remesa,     name="api_exportar_remesa"),
    path("api/conciliar/",                          views.api_conciliar,           name="api_conciliar"),

    # Bulk Import
    path("api/cargas/excel/",                       views.api_cargar_excel,        name="api_cargar_excel"),
]