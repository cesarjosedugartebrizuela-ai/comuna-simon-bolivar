from django.contrib import admin
from .models import Constancia
from unfold.admin import ModelAdmin
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

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
        
        descargar_url = f'/constancias/imprimir_constancia/{obj.pk}/' 

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

    def get_exclude(self, request, obj=None):
        # Obtenemos los campos excluidos por defecto de la clase padre
        excluded = super().get_exclude(request, obj) or []
        
        # Convertimos a lista por si viene como tupla, para poder modificarla
        excluded = list(excluded)

        # Si el usuario NO es administrador (superuser)
        if not request.user.is_superuser:
            # Lista de los nombres de los campos en tu modelo que queremos ocultar
            campos_a_ocultar = ['usuario', 'fecha_aprobacion', 'estatus', 'observaciones'] 
            
            # Agregamos cada campo a la lista de excluidos si no está allí
            for campo in campos_a_ocultar:
                if campo not in excluded:
                    excluded.append(campo)

        return excluded
    
    def save_model(self, request, obj, form, change):
        # Si 'change' es False, significa que estamos CREANDO una nueva constancia, no editando.
        if not change:
            # Verificamos si el usuario NO es un administrador
            if not request.user.is_superuser:
                # Asignamos el usuario que hizo la petición al campo 'usuario' del objeto
                obj.usuario = request.user 
                
        # Finalmente, llamamos al método original de Django para que guarde los datos en la base de datos
        super().save_model(request, obj, form, change)
        
    estado_y_acciones.short_description = 'Estado / Acciones'

    list_display = ['fecha_solicitud','fecha_aprobacion', 'motivo', 'estatus', 'observaciones', 'estado_y_acciones']
    pass