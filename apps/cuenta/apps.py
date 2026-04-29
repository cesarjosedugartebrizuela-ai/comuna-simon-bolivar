from django.apps import AppConfig


class CuentaConfig(AppConfig):
    name = 'apps.cuenta'
    label = 'cuenta'
    # Esta línea cambia el nombre de la sección en el menú lateral
    verbose_name = 'Autenticación y autorización'
