from ninja import Router
from django.contrib.auth import authenticate
from .schemas import LoginSchema, UserOutSchema
from configuracion_comuna.auth import crear_token_jwt, AuthBearer

router = Router()

@router.post("/login")
def login(request, data: LoginSchema):
    # Autenticamos usando el backend de Django
    user = authenticate(username=data.username, password=data.password)
    if user is not None:
        token = crear_token_jwt(user.id)
        return {"token": token, "mensaje": "Inicio de sesión exitoso"}
    return router.create_response(request, {"error": "Credenciales inválidas"}, status=401)

# Usamos AuthBearer para proteger esta ruta. ¡Solo usuarios con token pueden entrar!
@router.get("/me", response=UserOutSchema, auth=AuthBearer())
def perfil_usuario(request):
    # request.auth contiene el usuario que devolvió nuestra clase AuthBearer
    return request.auth