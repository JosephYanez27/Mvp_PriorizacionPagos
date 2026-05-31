from django.contrib import admin
from django.urls import path, include

from dashboard import views as tesoreria_views

urlpatterns = [

    path('admin/', admin.site.urls),

    # ── Módulos de Tesorería (vistas HTML) ───────────────────────────
    path('',              tesoreria_views.priorizacion, name='priorizacion'),
    path('confirmacion/', tesoreria_views.confirmacion, name='confirmacion'),
    path('conciliacion/', tesoreria_views.conciliacion, name='conciliacion'),
    path('auditoria/',    tesoreria_views.auditoria,    name='auditoria'),

    # ── APIs ─────────────────────────────────────────────────────────
    # facturas/urls.py tiene TODAS las rutas /api/... del sistema
    path('', include('facturas.urls')),

    # cargas y api quedan si tienen rutas propias adicionales
    path('api/facturas/', include('cargas.urls')),
    path('api/',          include('api.urls')),
]