from django.contrib import admin
from apps.cuenta.models import User as Usuario
from unfold.admin import ModelAdmin


@admin.register(Usuario)
class UsuarioAdmin(ModelAdmin):
    list_display = ['origen', 'cedula','nombre_completo']
