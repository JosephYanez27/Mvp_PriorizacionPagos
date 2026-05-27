from django.contrib import admin
from django.urls import path, include

from core import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('dashboard.urls')),
    path('', include('facturas.urls')),
    path(
    'auditoria/',
    include('auditoria.urls')
),
    
    # Por esta otra:
    path('api/facturas/', include('cargas.urls')), 

    path('api/', include('api.urls')),

]