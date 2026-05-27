from django.shortcuts import redirect

def auditar_proveedor(request, proveedor_id):

    return redirect(f'/?modulo=auditoria&proveedor={proveedor_id}')