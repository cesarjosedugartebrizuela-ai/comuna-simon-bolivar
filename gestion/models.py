from django.db import models
from datetime import date

class Usuario(models.Model):
    # Definimos las opciones
    OPCIONES_GENERO = [
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
    ]
    OPCIONES_ROL = [
        ('administrador', 'Administrador'),
        ('vecino', 'Vecino'),
    ]
    OPCIONES_ESTADO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    # Atributos (Campos)
    nombre_completo = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=15, choices=OPCIONES_GENERO)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    direccion = models.TextField()
    consejo_comunal = models.CharField(max_length=100)
    rol = models.CharField(max_length=15, choices=OPCIONES_ROL, default='vecino')
    estado = models.CharField(max_length=10, choices=OPCIONES_ESTADO, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    discapacidad = models.CharField(max_length=50, default='No Posee')
    intentos_recuperacion = models.IntegerField(default=0)
    bloqueo_hasta = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula_identidad})"

class Constancia(models.Model):
    # Definimos las opciones
    ESTATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]
    # Relacionamos la constancia con un usuario de la tabla Usuario
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
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

class CargaFamiliar(models.Model):
    # Definimos las opciones
    PARENTESCO_CHOICES = [
        ('Hijo/a', 'Hijo/a'),
        ('Sobrino/a', 'Sobrino/a'),
        ('Nieto/a', 'Nieto/a'),
        ('Otro', 'Otro'),
    ]
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
    nombre_completo = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=20, choices=PARENTESCO_CHOICES)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=15, choices=GENERO_CHOICES)
    discapacidad = models.CharField(max_length=50, default='No Posee')
    escolarizado = models.CharField(max_length=2, choices=ESCOLARIZADO_CHOICES, default='si')
    cedula_identidad = models.CharField(max_length=20, null=True, blank=True) # Opcional para niños
    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco})"
    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))