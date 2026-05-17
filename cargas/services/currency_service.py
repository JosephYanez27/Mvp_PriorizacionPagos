USD_TO_MXN = 19.50


def convertir_a_mxn(monto, moneda):

    if moneda is None:
        return monto

    moneda = moneda.upper()

    if moneda == 'USD':

        return monto * USD_TO_MXN

    return monto