from django.db.models import Sum, F
from facturas.models import Factura


def obtener_priorizacion_pagos():
    """
    Calcula el scoring de priorización de pagos basado en:
    - 60% Importancia del proveedor (estrellas)
    - 40% Urgencia de pago (días vencidos, máximo 60 días)
    
    Retorna una lista de proveedores ordenada por scoring descendente.
    """
    
    # 1. Agrupar facturas PENDIENTES por proveedor
    # Traemos nombre del proveedor, sus estrellas y el total acumulado
    proveedores_agrupados = Factura.objects.filter(
        estado='PENDIENTE'
    ).values(
        nombre=F('proveedor__nombre'),
        estrellas=F('proveedor__prioridad_estrellas')
    ).annotate(
        cantidad_a_pagar=Sum('total'),
        max_dias_vencidos=Sum('dias_vencidos')  # Sumamos los días vencidos
    ).order_by('proveedor')

    resultado = []

    for prov in proveedores_agrupados:
        estrellas = prov['estrellas'] or 3  # Default 3 si es nulo
        dias_vencidos = prov['max_dias_vencidos'] or 0
        
        # --- CÁLCULO DEL FACTOR TIEMPO ---
        # Normalizamos los días vencidos a una escala de 0 a 1
        # Máximo 60 días = factor 1.0
        if dias_vencidos <= 0:
            factor_tiempo = 0.0
        else:
            # Escala: 60 días = 1.0 (máxima urgencia)
            factor_tiempo = min(dias_vencidos / 60.0, 1.0)

        # --- CÁLCULO DEL FACTOR PROVEEDOR ---
        # Convertimos estrellas (1-5) a escala 0.2-1.0
        factor_proveedor = estrellas / 5.0

        # --- FÓRMULA FINAL DE SCORING ---
        # 60% peso proveedor (relación/importancia)
        # 40% peso tiempo (urgencia/vencimiento)
        peso_proveedor = 0.60
        peso_tiempo = 0.40
        
        score_calculado = (factor_proveedor * peso_proveedor) + (factor_tiempo * peso_tiempo)
        
        # Convertimos a porcentaje (0-100)
        scoring_final = int(score_calculado * 100)
        scoring_final = max(scoring_final, 0)  # Aseguramos no negativos

        # 2. Armar la estructura para el frontend
        resultado.append({
            "proveedor": prov['nombre'],
            "cantidad_a_pagar": float(prov['cantidad_a_pagar'] or 0),
            "prioridad_estrellas": estrellas,
            "dias_vencidos": dias_vencidos,
            "scoring": scoring_final  # 0-100
        })

    # 3. Ordenar por SCORING descendente (mayor peligro primero)
    resultado_ordenado = sorted(resultado, key=lambda x: x['scoring'], reverse=True)
    
    return resultado_ordenado
