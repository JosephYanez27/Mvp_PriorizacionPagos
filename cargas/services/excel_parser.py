import pandas as pd
import numpy as np

from .utils import limpiar_numero
from .currency_service import USD_TO_MXN, convertir_a_mxn


IGNORAR = [

    'CUENTA POR PAGAR',
    'TOTAL',
    'A1',
    'FECHA DE FACTURA'
]


# ======================================================
# DETECTAR FILAS TOTAL
# ======================================================

def es_total(texto):

    if pd.isna(texto):
        return False

    texto = str(texto).strip().upper()

    return texto.startswith("TOTAL")


# ======================================================
# DETECTAR FACTURAS
# ======================================================

def es_factura(texto):

    if pd.isna(texto):
        return False

    texto = str(texto).strip().upper()

    return texto.startswith("F-")


# ======================================================
# LIMPIAR TEXTO
# ======================================================

def limpiar_texto(valor):

    if pd.isna(valor):
        return None

    return str(valor).strip()


# ======================================================
# PARSER PRINCIPAL
# ======================================================

def leer_excel(path_archivo):

    df = pd.read_excel(
        path_archivo,
        header=None
    )

    facturas = []

    proveedor_actual = None

    for _, row in df.iterrows():

        primera_columna = row[0]

        # -------------------------------------------------
        # FILAS VACÍAS
        # -------------------------------------------------

        if pd.isna(primera_columna):
            continue

        texto = limpiar_texto(primera_columna)

        texto_upper = texto.upper()

        # -------------------------------------------------
        # IGNORAR ENCABEZADOS
        # -------------------------------------------------

        if any(x in texto_upper for x in IGNORAR):
            continue

        # -------------------------------------------------
        # IGNORAR TOTALES
        # -------------------------------------------------

        if es_total(texto):
            continue

        # -------------------------------------------------
        # DETECTAR FACTURA
        # -------------------------------------------------

        if es_factura(texto):

            try:

                fecha_factura = pd.to_datetime(
                row[1],
                dayfirst=True,
                errors='coerce'
                )

                monto_original = limpiar_numero(row[2])

                # -----------------------------------------
                # LEER MONEDA
                # -----------------------------------------

                moneda = limpiar_texto(row[3])

                if moneda is None:
                    moneda = 'MXN'

                moneda = moneda.upper().strip()

                if moneda not in ['MXN', 'USD']:
                    moneda = 'MXN'

                # -----------------------------------------
                # CONVERTIR A MXN
                # -----------------------------------------

                monto_mxn = convertir_a_mxn(
                    monto_original,
                    moneda
                )

                # -----------------------------------------
                # COLUMNAS FINANCIERAS
                # -----------------------------------------

                a_la_fecha = limpiar_numero(row[4])

                dias_30 = limpiar_numero(row[5])

                dias_60 = limpiar_numero(row[6])

                dias_90 = limpiar_numero(row[7])

                dias_120 = limpiar_numero(row[8])

                antiguos = limpiar_numero(row[9])

                total = limpiar_numero(row[10])

                # -----------------------------------------
                # CALCULAR TOTAL SI VIENE VACÍO
                # -----------------------------------------

                if total == 0:

                    total = (

                        a_la_fecha +
                        dias_30 +
                        dias_60 +
                        dias_90 +
                        dias_120 +
                        antiguos
                    )

                # -----------------------------------------
                # DETECTAR DÍAS VENCIDOS
                # -----------------------------------------

                dias_vencidos = 0

                if antiguos > 0:

                    dias_vencidos = 120

                elif dias_120 > 0:

                    dias_vencidos = 120

                elif dias_90 > 0:

                    dias_vencidos = 90

                elif dias_60 > 0:

                    dias_vencidos = 60

                elif dias_30 > 0:

                    dias_vencidos = 30

                # -----------------------------------------
                # CREAR OBJETO FACTURA
                # -----------------------------------------

                factura = {

                    'folio': texto,

                    'proveedor': proveedor_actual,

                    'fecha_factura': fecha_factura,

                    'moneda': moneda,

                    'monto_original': monto_original,

                    'tipo_cambio': (
                        USD_TO_MXN
                        if moneda == 'USD'
                        else 1
                    ),

                    'monto_mxn': monto_mxn,

                    'dias_vencidos': dias_vencidos,

                    'a_la_fecha': a_la_fecha,

                    'dias_30': dias_30,

                    'dias_60': dias_60,

                    'dias_90': dias_90,

                    'dias_120': dias_120,

                    'antiguos': antiguos,

                    'total': total
                }

                facturas.append(factura)

            except Exception as e:

                print(f"Error procesando fila: {texto}")

                print(e)

        else:

            # -------------------------------------------------
            # ES PROVEEDOR
            # -------------------------------------------------

            proveedor_actual = texto

    return facturas