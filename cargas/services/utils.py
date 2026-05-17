def limpiar_numero(valor):

    if valor is None:
        return 0

    if str(valor).strip() == '':
        return 0

    try:

        valor = str(valor)

        # quitar espacios
        valor = valor.strip()

        # formato europeo
        valor = valor.replace('.', '')

        valor = valor.replace(',', '.')

        return float(valor)

    except:

        return 0