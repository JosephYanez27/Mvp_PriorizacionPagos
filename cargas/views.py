from django.shortcuts import render


def vista_subida(request):

    return render(
        request,
        'cargas/subir_excel.html'
    )