from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.index,
        name='dashboard'
    ),

    path(
        'api/pagos/',
        views.vista_dashboard_pagos,
        name='dashboard_pagos'
    ),
]