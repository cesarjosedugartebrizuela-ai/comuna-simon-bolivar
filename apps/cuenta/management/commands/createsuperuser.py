from django.contrib.auth.management.commands import createsuperuser

class Command(createsuperuser.Command):
    help = 'Crea un superusuario sin pedir el campo username en la consola'

    def handle(self, *args, **options):
        # Al inyectar un valor aquí, Django cree que ya se lo dimos 
        # y se salta la pregunta del "Usuario:" en la consola.
        options['username'] = 'usuario_oculto'
        
        # Continuamos con el comportamiento normal del comando
        super().handle(*args, **options)