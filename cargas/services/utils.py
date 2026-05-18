import pandas as pd
import numpy as np


def limpiar_numero(valor):

    # -----------------------------------------
    # NULL / NaN
    # -----------------------------------------

    if valor is None:
        return 0

    if pd.isna(valor):
        return 0

    # -----------------------------------------
    # STRING
    # -----------------------------------------

    valor = str(valor).strip()

    if valor == '':
        return 0

    if valor.lower() == 'nan':
        return 0

    # -----------------------------------------
    # LIMPIEZA
    # -----------------------------------------

    valor = valor.replace('$', '')
    valor = valor.replace(' ', '')

    # formato europeo
    valor = valor.replace('.', '')
    valor = valor.replace(',', '.')

    # -----------------------------------------
    # CONVERTIR
    # -----------------------------------------

    try:

        numero = float(valor)

        if np.isnan(numero):
            return 0

        return numero

    except:

        return 0