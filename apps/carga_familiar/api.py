from ninja import Router
from typing import List
from apps.carga_familiar.models import CargaFamiliar, Parentesco
from apps.carga_familiar.schemas import CargaFamiliarOut, CargaFamiliarIn
from configuracion_comuna.auth import AuthBearer

router = Router(auth=AuthBearer())  # Protegemos TODAS las rutas de este router

@router.get("/", response=List[CargaFamiliarOut])
def listar_carga(request):
    # Devolvemos solo la carga familiar del usuario autenticado
    return CargaFamiliar.objects.filter(usuario=request.auth)

@router.post("/")
def crear_familiar(request, data: CargaFamiliarIn):
    try:
        parentesco = Parentesco.objects.get(id=data.parentesco_id)
        # Creamos el registro asignándolo al usuario del token
        familiar = CargaFamiliar.objects.create(
            usuario=request.auth,
            parentesco=parentesco,
            cedula_identidad=data.cedula_identidad,
            nombre_completo=data.nombre_completo,
            fecha_nacimiento=data.fecha_nacimiento,
            genero=data.genero,
            discapacidad=data.discapacidad,
            escolarizado=data.escolarizado
        )
        return {"mensaje": "Familiar registrado exitosamente", "id": familiar.id}
    except Parentesco.DoesNotExist:
        return router.create_response(request, {"error": "El parentesco no existe"}, status=404)