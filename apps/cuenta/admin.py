from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

from django.utils.html import format_html
from django.urls import reverse

# Importaciones específicas de Unfold
from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm as UnfoldUserChangeForm
from unfold.forms import AdminPasswordChangeForm
from unfold.decorators import display

from apps.cuenta.models import User, Grupo

# ---- AQUÍ DESREGISTRAMOS EL GRUPO ORIGINAL ----
admin.site.unregister(AuthGroup)

# ---- AQUÍ REGISTRAMOS TU NUEVO GRUPO CON ESTILOS DE UNFOLD ----
@admin.register(Grupo)
class GrupoAdmin(BaseGroupAdmin, ModelAdmin):
    pass

# Opcional: Desregistrar el modelo Group si no lo vas a usar
# from django.contrib.auth.models import Group
# admin.site.unregister(Group)

# 1. Usamos ModelForm normal para tener control total sin que Django exija contraseñas
class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('nombre_completo', 'email', 'cedula', 'origen')

    def save(self, commit=True):
        # Evitamos guardar inmediatamente para poder modificar el objeto antes
        user = super().save(commit=False)
        
        # Generación automática del username (Ejemplo: V-12345678)
        user.username = f"{user.origen}-{user.cedula}"
        
        # Como no pedimos contraseña al registrar, asignamos una inutilizable por seguridad
        # (Posteriormente podrás asignarle una desde el modo edición)
        user.set_unusable_password()
        
        if commit:
            user.save()
        return user


# El decorador @admin.register es la forma moderna de registrar modelos
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    # Asignamos los formularios
    add_form = UserCreateForm
    form = UnfoldUserChangeForm
    change_password_form = AdminPasswordChangeForm

    # Accesos directos del lado derecho
    @display(description="Editar")
    def editar(self, obj):
        url = reverse('admin:cuenta_user_change', args=[obj.id])
        return format_html(
            '<a class="font-medium text-primary-600 hover:text-primary-500" href="{}">Editar</a>', 
            url
        )
    
    @display(description="Eliminar")
    def eliminar(self, obj):
        url = reverse('admin:cuenta_user_delete', args=[obj.id])
        return format_html(
            '<a class="font-medium text-red-600 hover:text-red-500" href="{}">Eliminar</a>', 
            url
        )
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return True

    # ---- 2. FORMULARIO DE CREACIÓN (Solo los 4 campos requeridos) ----
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre_completo', 'email', 'cedula', 'origen')
        }),
    )
    
    readonly_fields = [
        'username', 'nombre_completo', 'last_login', 
        'fecha_registro', 'fecha_actualizacion', 'is_superuser'
    ]
    
    list_display = ('username', 'cedula', 'email', 'editar')
    list_filter = ('username', 'cedula', 'email')
    search_fields = ()
    list_display_links = None
    actions = None
    
    # ---- 3. FORMULARIO DE EDICIÓN CON PESTAÑAS ----
    # Se agregó 'classes': ['tab'] a cada diccionario para activar el modo Pestañas en Unfold
    fieldsets = (
        ('Credenciales', {
            'classes': ['tab'],
            'fields': ('username', 'origen', 'cedula', 'nombre_completo', 'email', 'password')
        }),
        ('Permisos', {
            'classes': ['tab'],
            'fields': ('is_staff', 'is_active')
        }),
        ('Grupos', {
            'classes': ['tab'],
            'fields': ('groups',)
        }),
        ('Actividad', {
            'classes': ['tab'],
            'fields': ('fecha_registro', 'fecha_actualizacion', 'last_login',)
        }),
    )