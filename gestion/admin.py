from django.contrib import admin
from .models import Usuario, Constancia, CargaFamiliar
from unfold.admin import ModelAdmin

#admin.site.register(Usuario)
#admin.site.register(Constancia)
#admin.site.register(CargaFamiliar)


@admin.register(Usuario)
class MyModelAdmin(ModelAdmin):
    list_display = ['nombre_completo', 'cedula_identidad']
    pass

@admin.register(Constancia)
class MyModelAdmin(ModelAdmin):
    
    pass