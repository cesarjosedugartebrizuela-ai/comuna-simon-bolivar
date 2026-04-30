from django.db import models
from apps.cuenta.models import User as Usuario
from apps.carga_familiar.models.parentesco import Parentesco
from datetime import date

class CargaFamiliar(models.Model):

    GENERO_CHOICES = [
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
    ]
    ESCOLARIZADO_CHOICES = [
        ('si', 'Sí'),
        ('no', 'No'),
    ]
    # Relación con el Usuario (Padre/Madre/Tutor)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='familiares')
    cedula_identidad = models.CharField(max_length=20, null=True, blank=True) # Opcional para niños
    nombre_completo = models.CharField(max_length=100)
    parentesco = models.ForeignKey(Parentesco, on_delete=models.CASCADE, related_name='cargas_familiares')
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=15, choices=GENERO_CHOICES)
    discapacidad = models.CharField(max_length=50, default='No Posee')
    escolarizado = models.BooleanField("Escolarizado", default=True)
    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco})"
    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    class Meta:
        managed             = True
        db_table            = 'carga_familiar\".\"carga_familiar'
        verbose_name        = 'Carga Familiar'
        verbose_name_plural = 'Cargas Familiares'