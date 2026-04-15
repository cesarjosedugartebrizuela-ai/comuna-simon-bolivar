from django.contrib import admin
from .models import Usuario, Constancia, CargaFamiliar
from unfold.admin import ModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html

@admin.register(Usuario)
class UsuarioAdmin(ModelAdmin):
    list_display = ['nombre_completo', 'cedula_identidad']

@admin.register(Constancia)
class ConstanciaAdmin(ModelAdmin):
    list_display = ['fecha_solicitud','fecha_aprobacion', 'motivo', 'estatus', 'observaciones', ]
    pass

@admin.register(CargaFamiliar)
class CargaFamiliarAdmin(ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        # Guardar la request para poder usarla desde el método de lista (permiso)
        self._request = request
        return super().changelist_view(request, extra_context)

    def acciones(self, obj):
        request = getattr(self, '_request', None)
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        change_url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])
        delete_url = reverse(f'admin:{app_label}_{model_name}_delete', args=[obj.pk])

        can_change = True
        can_delete = True
        if request is not None:
            can_change = request.user.has_perm(f'{app_label}.change_{model_name}')
            can_delete = request.user.has_perm(f'{app_label}.delete_{model_name}')

        parts = []
        if can_change:
            # Usamos clases de Tailwind: bg-yellow-500 (color), rounded-full (píldora), flex (para alinear el icono)
            btn_editar = f'''
                <a href="{change_url}" class="flex flex-row items-center gap-1 rounded-full bg-green-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-yellow-600" style="color: white; text-decoration: none;">
                    <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
                    Editar
                </a>
            '''
            parts.append(btn_editar)
            
        if can_delete:
            # Usamos bg-red-600 para el botón de eliminar
            btn_eliminar = f'''
                <a href="{delete_url}" class="flex flex-row items-center gap-1 rounded-full bg-red-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-red-700" style="color: white; text-decoration: none;">
                    <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                    Eliminar
                </a>
            '''
            parts.append(btn_eliminar)

        # Los envolvemos en un contenedor "flex" con "gap-2" para que, si aparecen ambos, tengan una pequeña separación entre ellos
        if parts:
            html_final = f'<div class="flex flex-row gap-2">{"".join(parts)}</div>'
            return mark_safe(html_final)
            
        return '-'
    acciones.short_description = 'Acciones'

    list_display = ['cedula_identidad', 'nombre_completo', 'parentesco', 'edad', 'escolarizado', 'discapacidad', 'acciones']