from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
import random


class UserManager(BaseUserManager):

    def create_user(self, email, origen, cedula, nombre_completo, password=None, **kwargs):

        kwargs.pop('username', None)

        if not cedula:
            raise ValueError('El usuario debe tener un su numero de cedula')
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        usuario = f'{origen}-{cedula}'

        email = self.normalize_email(email)
        user = self.model(
            username=usuario,
            email=email,
            origen=origen,
            cedula=cedula,
            nombre_completo=nombre_completo,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, origen, cedula, nombre_completo, password=None, **kwargs):
        user = self.create_user(
            email=email,
            origen=origen,
            cedula=cedula,
            nombre_completo=nombre_completo,
            password=password,
            **kwargs
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    ORIGEN = [
        ('V', 'V'),
        ('E', 'E'),
    ]

    CONSEJO_COMUNAL = [
        ('Andrés Bello', 'Andrés Bello'),
        ('Casco Historico', 'Casco Historico'),
        ('Panteón Nacional', 'Panteón Nacional'),
        ('Lomas de Urdaneta', 'Lomas de Urdaneta'),
        ('San José', 'San José'),
        ('La Pastora', 'La Pastora'),
        ('El Mirador', 'El Mirador'),
        ('Santa Teresa', 'Santa Teresa')
    ]

    OPCIONES_GENERO = [
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
    ]

    verificacion = models.CharField(max_length=10, blank=True, null=True)
    nombre_completo = models.CharField('Nom/Ape', max_length=255, blank=True, null=True)
    username = models.CharField('Usuario', max_length=20, unique=True)
    origen = models.CharField('Origen', max_length=1, choices=ORIGEN)
    cedula = models.IntegerField('Cédula')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=15, choices=OPCIONES_GENERO)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField('Correo', max_length=255, unique=True)
    direccion = models.TextField()
    consejo_comunal = models.CharField(max_length=100, choices=CONSEJO_COMUNAL)
    fecha_registro = models.DateTimeField('Fecha Registro', auto_now_add=True)
    discapacidad = models.BooleanField('Discapacidad', default=False)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)
    is_verified = models.BooleanField('VERIFICADO', default=True)
    is_active = models.BooleanField('ACTIVO', default=True)
    is_staff = models.BooleanField('STAFF', default=False)
    is_superuser = models.BooleanField('ROOT', default=False)

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.verificacion:
            self.verificacion = ''.join(str(random.randint(0, 9)) for _ in range(10))

        super().save(*args, **kwargs)


    class Meta:
        managed             = True
        db_table            = 'cuenta\".\"usuario'
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'
        unique_together     = ('origen','cedula')

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['origen','cedula','nombre_completo','email']

    def __str__(self):
        return self.username

class Grupo(Group):
    class Meta:
        proxy = True # ¡Esta es la magia que crea el espejo!
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'

class TokenListaNegra(models.Model):
    """
    Modelo para almacenar los tokens JWT que han sido invalidados mediante logout.
    """
    token = models.CharField(max_length=500, unique=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'cuenta"."token_lista_negra'
        verbose_name = 'Token en Lista Negra'
        verbose_name_plural = 'Tokens en Lista Negra'

    def __str__(self):
        return f"Token invalidado el {self.fecha_agregado}"

class Comuna(models.Model):
    origen = models.CharField(max_length=1)
    cedula = models.IntegerField()
    nombre_completo = models.CharField(max_length=255)
    consejo_comunal = models.CharField(max_length=100)

    class Meta:
        managed             = True
        db_table            = 'cuenta\".\"comuna'
        verbose_name        = 'Comuna'
        verbose_name_plural = 'Comunas'

    def __str__(self):
        return self.nombre_completo
