from ninja import Router
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from .schemas import LoginSchema, UserOutSchema, RecuperarPasswordSchema, RestablecerPasswordSchema
from configuracion_comuna.auth import crear_token_jwt, AuthBearer
from .models import User, TokenListaNegra

router = Router()

@router.post("/login", response={200: dict, 401: dict})
def login(request, data: LoginSchema):
    # Autenticamos usando el backend de Django
    user = authenticate(username=data.username, password=data.password)
    if user is not None:
        token = crear_token_jwt(user.id)
        return {"token": token, "mensaje": "Inicio de sesión exitoso"}
    return 401, {"error": "Credenciales inválidas"}

@router.post("/logout", auth=AuthBearer())
def logout(request):
    """
    Endpoint para cerrar sesión de forma segura.
    Extrae el token de la petición y lo guarda en la lista negra.
    """
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token_string = auth_header.split(" ")[1] 
        
        # get_or_create evita errores si por alguna razón se envía dos veces
        TokenListaNegra.objects.get_or_create(token=token_string)

    return {"mensaje": "Sesión cerrada exitosamente. El token ha sido invalidado."}

# Usamos AuthBearer para proteger esta ruta. ¡Solo usuarios con token pueden entrar!
@router.get("/perfil", response=UserOutSchema, auth=AuthBearer())
def perfil_usuario(request):
    # request.auth contiene el usuario que devolvió nuestra clase AuthBearer
    return request.auth

@router.post("/recuperar-password")
def solicitar_recuperacion(request, data: RecuperarPasswordSchema):
    """
    Paso 1: El usuario envía su email. Generamos un token temporal y (simulamos) enviar un correo.
    """
    user = User.objects.filter(email=data.email).first()
    
    if user:
        # Generamos un token seguro que expira y es de un solo uso
        token = default_token_generator.make_token(user)
        id = user.id
        
        return {"mensaje": f"Si el correo {data.email} está registrado. Token : {token} y id : {id}"}
    else:
        return f"El correo {data.email} no se encuentra registrado."

@router.post("/restablecer-password")
def restablecer_password(request, data: RestablecerPasswordSchema):
    """
    Paso 2: La app móvil envía el ID del usuario, el token recibido por correo y la nueva contraseña.
    """
    user = User.objects.filter(id=data.id).first()
    
    # Comprobamos que el usuario exista y que el token enviado coincida y sea válido
    if user is not None and default_token_generator.check_token(user, data.token):
        # Guardamos la nueva contraseña encriptada correctamente
        user.set_password(data.nuevo_password)
        user.save()
        return {"mensaje": "La contraseña ha sido actualizada exitosamente."}
        
    return router.create_response(
        request, 
        {"error": "El enlace de recuperación es inválido o ha caducado."}, 
        status=400
    )