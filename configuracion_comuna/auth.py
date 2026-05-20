import jwt
from datetime import datetime, timedelta
from django.conf import settings
from ninja.security import HttpBearer
from apps.cuenta.models import User  

# Esta clase protegerá nuestras rutas
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Decodificamos el token usando la clave secreta de tu proyecto Django
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            return user  # Si todo sale bien, retornamos el usuario
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None  # Si el token es inválido o expiró, denegamos el acceso

# Función auxiliar para crear el token
def crear_token_jwt(user_id):
    payload = {
        'user_id': user_id,
        # El token expirará en 1 día
        'exp': datetime.now() + timedelta(days=1),
        'iat': datetime.now()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")