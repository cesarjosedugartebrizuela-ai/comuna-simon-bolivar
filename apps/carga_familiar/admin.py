from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

# Importaciones de Unfold
from unfold.admin import ModelAdmin
from unfold.decorators import display

from apps.carga_familiar.models import CargaFamiliar, Parentesco

@admin.register(CargaFamiliar)
class CargaFamiliarAdmin(ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        self._request = request
        return super().changelist_view(request, extra_context)
    
    # -----------------------------------------------------------
    # 1. LÓGICA DE BOTONES VISUALES (Unfold)
    # -----------------------------------------------------------
    @display(description="Acción")
    def ver_detalle(self, obj):
        # Genera la URL dinámica sin importar si hay errores de tipeo en el nombre de la app
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html(
            '<a class="font-medium text-primary-600 hover:text-primary-500" href="{}">Ver a detalle</a>', 
            url
        )

    @display(description="Acción")
    def editar(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return format_html(
            '<a class="font-medium text-primary-600 hover:text-primary-500" href="{}">Editar</a>', 
            url
        )

    # -----------------------------------------------------------
    # 2. COLUMNAS DINÁMICAS SEGÚN EL ROL
    # -----------------------------------------------------------
    def get_list_display(self, request):
        # Si es superusuario (Admin), ve a quién pertenece y el botón "Ver a detalle"
        if request.user.groups.filter(name='Admin').exists():
            return ('nombre_completo', 'usuario', 'parentesco', 'edad', 'ver_detalle')
        
        # Si es vecino, no necesita ver de quién es (ya sabe que es suyo) y ve "Editar"
        return ('nombre_completo', 'parentesco', 'edad', 'editar')

    # -----------------------------------------------------------
    # 3. FILTRADO DE DATOS (Quién ve qué)
    # -----------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si es Admin, retornamos todas las cargas familiares
        if request.user.is_superuser:
            return qs
        
        # Si es vecino, filtramos para que solo vea las suyas
        return qs.filter(usuario=request.user)

    # -----------------------------------------------------------
    # 4. FORMULARIO DINÁMICO (Ocultar campo usuario al vecino)
    # -----------------------------------------------------------
    def get_fieldsets(self, request, obj=None):
        # Formulario para el Admin (Puede elegir a qué usuario asignarle la carga)
        if request.user.is_superuser:
            return (
                ('Información General', {
                    'fields': ('usuario', 'nombre_completo', 'cedula_identidad', 'parentesco')
                }),
                ('Detalles Adicionales', {
                    'fields': ('fecha_nacimiento', 'genero', 'discapacidad', 'escolarizado')
                }),
            )
        
        # Formulario para el Vecino (No se le muestra el campo 'usuario')
        return (
            ('Información General', {
                'fields': ('nombre_completo', 'cedula_identidad', 'parentesco')
            }),
            ('Detalles Adicionales', {
                'fields': ('fecha_nacimiento', 'genero', 'discapacidad', 'escolarizado')
            }),
        )

    # -----------------------------------------------------------
    # 5. AUTO-COMPLETAR EL USUARIO AL GUARDAR
    # -----------------------------------------------------------
    def save_model(self, request, obj, form, change):
        # Si NO es superusuario (es decir, es vecino), le asignamos su propia cuenta
        if not request.user.is_superuser:
            obj.usuario = request.user
            
        # Finalmente, guardamos en la base de datos de forma normal
        super().save_model(request, obj, form, change)

@admin.register(Parentesco)
class ParentescoAdmin(ModelAdmin):
    list_display = ('descripcion', 'estatus')
    list_filter = ('estatus',)