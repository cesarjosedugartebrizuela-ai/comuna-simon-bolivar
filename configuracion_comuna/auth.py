import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from ninja.security import HttpBearer, django_auth
from apps.cuenta.models import User, TokenListaNegra

# Esta clase protegerá nuestras rutas
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if TokenListaNegra.objects.filter(token=token).exists():
            return None
        try:
            # Decodificamos el token usando la clave secreta de tu proyecto Django
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            return user  
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None 

SessionAuth = django_auth

# Función auxiliar para crear el token
def crear_token_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30), # el uso de timezone.utc asegura que la fecha sea consciente de la zona horaria
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")