from ninja import ModelSchema, Schema
from .models import Constancia

class ConstanciaOut(ModelSchema):
    class Meta:
        model = Constancia
        fields = ['id', 'fecha_solicitud', 'anios_residencia', 'motivo', 'estatus', 'observaciones']

class ConstanciaIn(Schema):
    anios_residencia: int
    motivo: str