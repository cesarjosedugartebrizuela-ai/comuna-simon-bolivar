from ninja import ModelSchema, Schema
from .models import CargaFamiliar, Parentesco

class CargaFamiliarOut(ModelSchema):
    # Hacemos un esquema de salida para mostrar los datos
    class Meta:
        model = CargaFamiliar
        fields = ['id', 'nombre_completo', 'fecha_nacimiento', 'genero', 'discapacidad', 'escolarizado']

# Esquema para registrar un nuevo familiar (Input)
class CargaFamiliarIn(Schema):
    cedula_identidad: str = None
    nombre_completo: str
    parentesco_id: int  # Pedimos el ID del parentesco
    fecha_nacimiento: str
    genero: str
    discapacidad: str = 'No Posee'
    escolarizado: bool = True