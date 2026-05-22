from ninja import Schema, ModelSchema
from apps.cuenta.models import User

# Esquema para recibir los datos de inicio de sesión
class LoginSchema(Schema):
    username: str
    password: str

# Esquema para devolver los datos del usuario (excluimos la contraseña por seguridad)
class UserOutSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'nombre_completo', 'email', 'cedula', 'origen', 'verificacion']

class RecuperarPasswordSchema(Schema):
    email: str

class RestablecerPasswordSchema(Schema):
    id: int       
    token: str    
    nuevo_password: str