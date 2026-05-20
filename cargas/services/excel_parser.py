import pandas as pd
from django.utils import timezone
from decimal import Decimal
from facturas.models import Proveedor, Factura
from .utils import limpiar_numero  # Mantenemos tu función de limpieza numérica
from .currency_service import USD_TO_MXN, convertir_a_mxn

IGNORAR = [
    'CUENTA POR PAGAR',
    'TOTAL',
    'A1',
    'FECHA DE FACTURA'
]

def es_total(texto):
    if pd.isna(texto):
        return False
    texto = str(texto).strip().upper()
    return texto.startswith("TOTAL")

def es_factura(texto):
    if pd.isna(texto):
        return False
    texto = str(texto).strip().upper()
    return texto.startswith("F-")

def limpiar_texto(valor):
    if pd.isna(valor):
        return None
    return str(valor).strip()

def leer_excel(path_archivo):
    """
    Lee el archivo Excel transaccional, identifica proveedores y folios,
    y guarda directamente los registros en la base de datos de PostgreSQL.
    """
    df = pd.read_excel(path_archivo, header=None)
    
    proveedor_actual_obj = None
    facturas_creadas = 0

    for _, row in df.iterrows():
        primera_columna = row[0]

        # 1. FILAS VACÍAS
        if pd.isna(primera_columna):
            continue

        texto = limpiar_texto(primera_columna)
        texto_upper = texto.upper()

        # 2. ENCABEZADOS Y TOTALES A IGNORAR
        if any(x in texto_upper for x in IGNORAR) or es_total(texto):
            continue

        # 3. DETECTAR FACTURA (LÓGICA OPERATIVA)
        if es_factura(texto):
            # Si se encuentra una factura antes de capturar un proveedor, evitamos un error
            if not proveedor_actual_obj:
                continue

            try:
                # Extraer la fecha real de la columna 1
                fecha_cruda = row[1]
                fecha_factura = pd.to_datetime(
                    fecha_cruda,
                    dayfirst=True,
                    errors='coerce'
                )
                
                # Si la fecha es válida, se extrae solo el objeto date para evitar desfases de zona horaria
                if not pd.isna(fecha_factura):
                    fecha_factura = fecha_factura.date()
                else:
                    fecha_factura = None

                # Leer montos originales
                monto_orig_val = limpiar_numero(row[2])
                monto_original = Decimal(str(monto_orig_val))

                # Extraer y normalizar divisa
                moneda = limpiar_texto(row[3])
                if moneda is None:
                    moneda = 'MXN'
                moneda = moneda.upper().strip()
                if moneda not in ['MXN', 'USD']:
                    moneda = 'MXN'

                # Asignar tipo de cambio dinámico
                tipo_cambio = Decimal(str(USD_TO_MXN)) if moneda == 'USD' else Decimal('1.00')

                # Calcular contravalor en pesos usando tu service original
                monto_mxn_val = convertir_a_mxn(monto_orig_val, moneda)
                monto_mxn = Decimal(str(monto_mxn_val))

                # Leer monto total de la obligación (Columna 10)
                total_val = limpiar_numero(row[10])
                
                # Si viene vacío o en 0, realizamos tu suma matemática de respaldo
                if total_val == 0:
                    a_la_fecha = limpiar_numero(row[4])
                    dias_30 = limpiar_numero(row[5])
                    dias_60 = limpiar_numero(row[6])
                    dias_90 = limpiar_numero(row[7])
                    dias_120 = limpiar_numero(row[8])
                    antiguos = limpiar_numero(row[9])
                    total_val = (a_la_fecha + dias_30 + dias_60 + dias_90 + dias_120 + antiguos)

                total = Decimal(str(total_val))

                # 4. CONDICIÓN COMERCIAL AUTOMÁTICA
                # Si el folio incluye indicios o es de contado, se asigna. Por defecto es CREDITO.
                tipo_pago = 'CREDITO'
                if 'CONTADO' in texto_upper or total_val <= 0:
                    tipo_pago = 'CONTADO'

                # 5. PERSISTENCIA EN POSTGRESQL (EVITAR DUPLICADOS POR FOLIO)
                # Al usar update_or_create, si vuelven a subir el mismo Excel, actualiza los montos
                # sin corromper el estado, las estrellas o las notas que ya capturó el auditor.
                Factura.objects.update_or_create(
                    folio=texto,
                    defaults={
                        'proveedor': proveedor_actual_obj,
                        'tipo_pago': tipo_pago,
                        'moneda': moneda,
                        'monto_original': monto_original,
                        'monto_mxn': monto_mxn,
                        'tipo_cambio': tipo_cambio,
                        'fecha_factura': fecha_factura,
                        'total': total,
                        # No alteramos el total_abonado ni el estado si la factura ya existía en el sistema
                    }
                )
                facturas_creadas += 1

            except Exception as e:
                print(f"Error procesando e insertando folio {texto}: {str(e)}")

        # 6. ES UN REGISTRO DE PROVEEDOR
        else:
            # Buscamos si el proveedor ya existe en el catálogo maestro para no alterar sus estrellas.
            # Si no existe, lo crea con el valor por defecto de 3.0 estrellas para que puedas calificarlo después.
            proveedor_obj, _ = Proveedor.objects.get_or_create(
                nombre=texto,
                defaults={'prioridad_estrellas': Decimal('3.0'), 'activo': True}
            )
            proveedor_actual_obj = proveedor_obj

    return facturas_creadas