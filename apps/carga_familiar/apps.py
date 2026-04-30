from django.apps import AppConfig


class CargaFamiiarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Asegúrate de que coincida con el nombre real de tu carpeta
    name = 'apps.carga_familiar' 
    label = 'carga_familiar'
    # Esta línea es la que hace la magia visual:
    verbose_name = 'Carga Familiar'
