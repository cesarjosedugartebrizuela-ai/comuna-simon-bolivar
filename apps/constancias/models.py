from django.db import models
from gestion.models import Usuario

class Constancia(models.Model):
    # Definimos las opciones
    ESTATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]
    # Relacionamos la constancia con un usuario de la tabla Usuario
    usuario = models.ForeignKey(Usuario, related_name='cedula_identidad', on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    anios_residencia = models.IntegerField(default=1)
    motivo = models.TextField()
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='Pendiente')
    observaciones = models.TextField(blank=True, null=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.usuario} ({self.fecha_aprobacion})"
    
    def __clase__(self):
        return f"Constancia {self.id} - {self.usuario.nombre_completo}"
