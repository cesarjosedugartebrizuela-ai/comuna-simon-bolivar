from django.contrib import admin
from .models import Usuario, Constancia, CargaFamiliar
from unfold.admin import ModelAdmin
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
#from django.contrib.admin import ModelAdmin

@admin.register(Usuario)
class UsuarioAdmin(ModelAdmin):
    list_display = ['nombre_completo', 'cedula_identidad']

@admin.register(Constancia)
class ConstanciaAdmin(ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        self._request = request
        return super().changelist_view(request, extra_context)

    # Ruta de los botones
    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('<int:pk>/Aprobada/', self.admin_site.admin_view(self.aprobar_constancia), name='%s_%s_aprobar' % info),
            path('<int:pk>/Rechazada/', self.admin_site.admin_view(self.rechazar_constancia), name='%s_%s_rechazar' % info),
        ]
        return custom_urls + urls

    def aprobar_constancia(self, request, pk):
        obj = self.get_object(request, pk)
        if obj:
            obj.estatus = 'Aprobada'  
            obj.fecha_aprobacion = timezone.now()
            obj.save()
            self.message_user(request, 'Constancia aprobada exitosamente.', messages.SUCCESS)
        
        info = self.model._meta.app_label, self.model._meta.model_name
        return redirect(f'admin:{info[0]}_{info[1]}_changelist')

    def rechazar_constancia(self, request, pk):
        obj = self.get_object(request, pk)
        if obj:
            obj.estatus = 'Rechazada' 
            obj.save()
            self.message_user(request, 'La constancia ha sido rechazada.', messages.WARNING)
            
        info = self.model._meta.app_label, self.model._meta.model_name
        return redirect(f'admin:{info[0]}_{info[1]}_changelist')

    def estado_y_acciones(self, obj):
        request = getattr(self, '_request', None)
        if not request:
            return '-'

        # Determinamos si el usuario es administrador
        es_admin = request.user.is_superuser 
        
        estatus_actual = str(obj.estatus).lower() 

        # Rutas de los botones de acción
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        aprobar_url = reverse(f'admin:{app_label}_{model_name}_aprobar', args=[obj.pk])
        rechazar_url = reverse(f'admin:{app_label}_{model_name}_rechazar', args=[obj.pk])
        
        descargar_url = reverse('imprimir_constancia', args=[obj.pk]) 

        # --- BLOQUES HTML REUTILIZABLES ---
        html_descargar = f'''
            <a href="{descargar_url}" target="_blank" class="flex flex-row items-center gap-1 rounded-full bg-blue-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-blue-700" style="color: white; text-decoration: none; width: max-content;">
                <span class="material-symbols-outlined" style="font-size: 16px;">download</span>
                Descargar
            </a>
        '''
        html_rechazada = '<span class="text-red-600 font-bold tracking-wide">Rechazada</span>'
        html_en_proceso = '<span class="text-gray-500 font-bold tracking-wide">En proceso</span>'

        if es_admin:
            if estatus_actual in ['en espera', 'espera', 'pendiente']:
                btn_aprobar = f'''
                    <a href="{aprobar_url}" class="flex flex-row items-center gap-1 rounded-full bg-green-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-green-700" style="color: white; text-decoration: none;">
                        <span class="material-symbols-outlined" style="font-size: 16px;">check_circle</span>
                        Aprobar
                    </a>
                '''
                btn_rechazar = f'''
                    <a href="{rechazar_url}" class="flex flex-row items-center gap-1 rounded-full bg-red-600 px-3 py-1 text-xs font-medium text-white shadow-sm hover:bg-red-700" style="color: white; text-decoration: none;">
                        <span class="material-symbols-outlined" style="font-size: 16px;">cancel</span>
                        Rechazar
                    </a>
                '''
                return mark_safe(f'<div class="flex flex-row gap-2">{btn_aprobar}{btn_rechazar}</div>')
            
            elif estatus_actual == 'aprobada':
                return mark_safe(html_descargar)
            
            elif estatus_actual == 'rechazada':
                return mark_safe(html_rechazada)

        else:
            if estatus_actual in ['en espera', 'espera', 'pendiente']:
                return mark_safe(html_en_proceso)
            
            elif estatus_actual == 'aprobada':
                return mark_safe(html_descargar)
            
            elif estatus_actual == 'rechazada':
                return mark_safe(html_rechazada)

        return '-'
        
    estado_y_acciones.short_description = 'Estado / Acciones'

    list_display = ['fecha_solicitud','fecha_aprobacion', 'motivo', 'estatus', 'observaciones', 'estado_y_acciones']
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