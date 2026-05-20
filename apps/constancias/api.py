from ninja import Router
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import os
from .models import Constancia
from .schemas import ConstanciaIn, ConstanciaOut
from configuracion_comuna.auth import AuthBearer

router = Router(auth=AuthBearer())

@router.post("/", response=ConstanciaOut)
def solicitar_constancia(request, data: ConstanciaIn):
    constancia = Constancia.objects.create(
        usuario=request.auth,
        anios_residencia=data.anios_residencia,
        motivo=data.motivo
    )
    return constancia

@router.get("/{constancia_id}/descargar")
def descargar_pdf(request, constancia_id: int):
    # Verificamos que la constancia exista y pertenezca al usuario
    constancia = get_object_or_404(Constancia, id=constancia_id, usuario=request.auth)
    
    # IMPORTANTE: Aquí llamas a tu función actual que genera o busca el PDF
    # Supongamos que tienes una ruta al archivo generado:
    ruta_al_pdf = f"/ruta/a/tus/pdfs/constancia_{constancia.id}.pdf" 
    
    # Si usas ReportLab u otra librería para generar el PDF al vuelo, 
    # puedes pasar el "buffer" directamente al FileResponse.
    
    if os.path.exists(ruta_al_pdf):
        archivo = open(ruta_al_pdf, 'rb')
        response = FileResponse(archivo, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="constancia_{constancia.id}.pdf"'
        return response
    else:
        return router.create_response(request, {"error": "PDF no encontrado o en proceso"}, status=404)