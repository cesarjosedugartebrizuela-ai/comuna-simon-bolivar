from .models import CargaFamiliar, Usuario, Constancia
from datetime import date
from datetime import datetime
from django.db.models import Count, Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

import base64
import datetime
import io
import locale
import os
import pytz
import qrcode

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass

def login_view(request):
    if request.method == 'POST':
        cedula_ingresada = request.POST.get('usuario')
        clave_ingresada = request.POST.get('password')
        try:
            # Buscamos al usuario por cédula
            user = Usuario.objects.get(cedula_identidad=cedula_ingresada)
            # Validamos la contraseña usando la lógica pura de Django
            if check_password(clave_ingresada, user.password):
                request.session['usuario_id'] = user.id
                request.session['rol'] = user.rol
                return redirect('dashboard')
            else:
                messages.error(request, "Contraseña incorrecta")
        except Usuario.DoesNotExist:
            messages.error(request, "La cédula no está registrada")
    return render(request, 'gestion/login.html')

def registro_view(request):
    if request.method == 'POST':
        # 1. Obtener datos del formulario
        nombre = request.POST.get('nombre')
        cedula_raw = request.POST.get('cedula').upper().strip().replace('.', '').replace(' ', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # 2. Validar si ya existe (Cédula o Email)
        if Usuario.objects.filter(cedula_identidad=cedula_raw).exists() or Usuario.objects.filter(email=email).exists():
            messages.error(request, "⚠️ La cédula o el correo ya están registrados.")
        else:
            # 3. Crear el nuevo usuario
            try:
                nuevo_usuario = Usuario(
                    nombre_completo=nombre,
                    cedula_identidad=cedula_raw,
                    fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                    genero=request.POST.get('genero'),
                    telefono=request.POST.get('telefono'),
                    email=email,
                    password=make_password(password), # Guardamos el hash de Django
                    direccion=request.POST.get('direccion'),
                    consejo_comunal=request.POST.get('consejo_comunal'),
                    discapacidad=request.POST.get('discapacidad'),
                    rol='vecino' # Por defecto todos son vecinos
                )
                nuevo_usuario.save()
                messages.success(request, "✅ Registro exitoso. Ya puedes iniciar sesión.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error al registrar: {e}")
    return render(request, 'gestion/registro.html')


def dashboard_view(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = Usuario.objects.get(id=usuario_id)
    todas_mis_constancias = Constancia.objects.filter(
        usuario=usuario,
    ).order_by('-fecha_solicitud')
    context = {
        'usuario': usuario,
        'constancias_listas': todas_mis_constancias
    }
    return render(request, 'gestion/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def editar_usuario_view(request, pk):
    try:
        usuario_editar = Usuario.objects.get(id=pk)
        if request.method == 'POST':
            usuario_editar.nombre_completo = request.POST.get('nombre_completo')
            usuario_editar.cedula_identidad = request.POST.get('cedula_identidad')
            usuario_editar.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            usuario_editar.genero = request.POST.get('genero')
            usuario_editar.email = request.POST.get('email')
            usuario_editar.telefono = request.POST.get('telefono')
            usuario_editar.discapacidad = request.POST.get('discapacidad')
            usuario_editar.consejo_comunal = request.POST.get('consejo_comunal')
            usuario_editar.direccion = request.POST.get('direccion')
            nueva_pass = request.POST.get('nueva_password')
            if nueva_pass:
                usuario_editar.password = make_password(nueva_pass)
            usuario_editar.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect('editar_usuario', pk=pk) 
        return render(request, 'gestion/ficha_usuario.html', {'perfil': usuario_editar})
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('dashboard')

def solicitar_constancia_view(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        user_obj = Usuario.objects.get(id=usuario_id)
        motivo_tramite = request.POST.get('motivo')
        anios = request.POST.get('anios_residencia')
        # Se crea el registro en la base de datos
        nueva_solicitud = Constancia(
            usuario=user_obj,
            motivo=motivo_tramite,
            anios_residencia=anios,
            estatus='Pendiente'
        )
        nueva_solicitud.save()
        messages.success(request, "✅ Solicitud enviada. Espere a que el administrador la valide.")
        return redirect('dashboard')
    return render(request, 'gestion/solicitar_constancia.html')

def registrar_carga_view(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    familiares = CargaFamiliar.objects.filter(usuario=usuario)
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        cedula_f = request.POST.get('cedula_identidad', '').strip()
        fecha_nac = request.POST.get('fecha_nacimiento')
        # --- VALIDACIONES ---
        if cedula_f:
            if CargaFamiliar.objects.filter(usuario=usuario, cedula_identidad=cedula_f).exists():
                messages.error(request, f"La cédula {cedula_f} ya está registrada en tu carga.")
                return render(request, 'gestion/registrar_carga.html', {'familiares': familiares})
        if CargaFamiliar.objects.filter(usuario=usuario, nombre_completo__iexact=nombre, fecha_nacimiento=fecha_nac).exists():
            messages.error(request, f"El familiar {nombre} ya está registrado.")
            return render(request, 'gestion/registrar_carga.html', {'familiares': familiares})
        CargaFamiliar.objects.create(
            usuario=usuario,
            nombre_completo=nombre,
            parentesco=request.POST.get('parentesco'),
            fecha_nacimiento=fecha_nac,
            genero=request.POST.get('genero'),
            discapacidad=request.POST.get('discapacidad'),
            escolarizado=request.POST.get('escolarizado'),
            cedula_identidad=cedula_f or None
        )
        messages.success(request, "Familiar registrado con éxito.")
        return redirect('registrar_carga')
    return render(request, 'gestion/registrar_carga.html', {'familiares': familiares})

def editar_carga_view(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    familiar = get_object_or_404(CargaFamiliar, pk=pk, usuario_id=usuario_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        cedula_f = request.POST.get('cedula_identidad', '').strip()
        fecha_nac = request.POST.get('fecha_nacimiento')
        # --- VALIDACIÓN AL EDITAR ---
        # Validar que la cédula no la tenga OTRO familiar del mismo usuario
        if cedula_f:
            if CargaFamiliar.objects.filter(usuario=usuario, cedula_identidad=cedula_f).exclude(pk=pk).exists():
                messages.error(request, f"La cédula {cedula_f} ya está asignada a otro familiar.")
                return render(request, 'gestion/editar_carga.html', {'familiar': familiar})
        # Validar Nombre + Fecha (excluyendo al actual)
        if CargaFamiliar.objects.filter(usuario=usuario, nombre_completo__iexact=nombre, fecha_nacimiento=fecha_nac).exclude(pk=pk).exists():
            messages.error(request, "Ya existe otro familiar con el mismo nombre y fecha de nacimiento.")
            return render(request, 'gestion/editar_carga.html', {'familiar': familiar})
        # Actualizamos los campos
        familiar.nombre_completo = nombre
        familiar.cedula_identidad = cedula_f or None
        familiar.parentesco = request.POST.get('parentesco')
        familiar.fecha_nacimiento = fecha_nac
        familiar.genero = request.POST.get('genero')
        familiar.discapacidad = request.POST.get('discapacidad')
        familiar.escolarizado = request.POST.get('escolarizado')
        familiar.save()
        messages.success(request, f"Datos de {familiar.nombre_completo} actualizados.")
        return redirect('registrar_carga')
    return render(request, 'gestion/editar_carga.html', {'familiar': familiar})

def eliminar_carga_view(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    # Seguridad: Solo puede eliminar si el familiar le pertenece a este usuario
    familiar = get_object_or_404(CargaFamiliar, pk=pk, usuario_id=usuario_id)
    nombre = familiar.nombre_completo
    familiar.delete()
    messages.success(request, f"Se ha eliminado a {nombre} de tu carga familiar.")
    return redirect('registrar_carga')

def lista_vecinos_view(request):
    busqueda = request.GET.get('buscar_cedula', '')
    if busqueda:
        # Filtramos si la cédula contiene el texto buscado
        vecinos = Usuario.objects.filter(cedula_identidad__icontains=busqueda).order_by('cedula_identidad')
    else:
        # Si no hay búsqueda, traemos todos
        vecinos = Usuario.objects.all().order_by('cedula_identidad')
    return render(request, 'gestion/lista_vecinos.html', {
        'vecinos': vecinos,
        'valor_busqueda': busqueda # Para mantener el texto en el input tras buscar
    })

def validar_constancias_view(request):
    busqueda = request.GET.get('buscar_cedula', '')
    if busqueda:
        # Filtramos las constancias por la cédula del usuario relacionado
        solicitudes = Constancia.objects.filter(
            usuario__cedula_identidad__icontains=busqueda
        ).order_by('-fecha_solicitud')
    else:
        solicitudes = Constancia.objects.all().order_by('-fecha_solicitud')
    return render(request, 'gestion/validar_constancias.html', {
        'solicitudes': solicitudes,
        'valor_busqueda': busqueda
    })

def cambiar_estatus_constancia(request, pk, nuevo_estatus):
    if request.session.get('rol') == 'administrador':
        constancia = get_object_or_404(Constancia, pk=pk)
        constancia.estatus = nuevo_estatus
        if nuevo_estatus == 'Aprobada':
            constancia.fecha_aprobacion = timezone.now()
        constancia.save()
        messages.success(request, f"Solicitud de {constancia.usuario.nombre_completo} marcada como {nuevo_estatus}.")
    return redirect('validar_constancias')

def generar_pdf_constancia(request, pk):
    usuario_id = request.session.get('usuario_id')
    # Solo se genera si está aprobada
    constancia = get_object_or_404(Constancia, pk=pk, estatus='Aprobada')
    usuario = constancia.usuario
    if constancia.usuario.id != usuario_id and request.session.get('rol') != 'administrador':
        return HttpResponse("No tiene permiso para ver este documento.", status=403)
    venezuela_tz = pytz.timezone('America/Caracas')
    fecha_referencia = constancia.fecha_aprobacion if constancia.fecha_aprobacion else constancia.fecha_solicitud
    fecha_local = fecha_referencia.astimezone(venezuela_tz)
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    # Creamos el contenido del QR
    datos_qr = (
        f"https://miurl.com/usuario.origen/usuario.cedula"+
        f"ID: {constancia.id}\n"
        f"Beneficiario: {usuario.nombre_completo}\n"
        f"Cédula: {usuario.cedula_identidad}\n"
        f"Aprobado el: {fecha_local.strftime('%d/%m/%Y')}\n"
        f"Validado por: Circuito Comunal Simón Bolívar"
    )
    # Generar el QR
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(datos_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    # Convertir la imagen a Base64 para que el HTML la entienda directamente
    buffer = io.BytesIO()
    img_qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    ruta_logo_fisica = os.path.join(settings.BASE_DIR, 'gestion', 'static', 'gestion', 'Logo2.png')
    context = {
        'u': usuario,
        'c': constancia,
        'fecha_dia': fecha_local.day,
        'fecha_mes': meses[fecha_local.month],
        'fecha_anio': fecha_local.year,
        'id_registro': f"00{usuario.id}",
        'ruta_logo': ruta_logo_fisica,
        'qr_code': qr_base64
    }
    html_string = render_to_string('gestion/pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Constancia_{usuario.cedula_identidad}.pdf"'
    # xhtml2pdf sabe interpretar rutas físicas de archivos si están bien formadas
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

def panel_estadisticas_view(request):
    if request.session.get('rol') != 'administrador':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')
    # Capturamos el filtro del consejo comunal
    consejo_seleccionado = request.GET.get('consejo_comunal', '')
    today = date.today()
    fem = [0, 0, 0, 0]
    masc = [0, 0, 0, 0]
    # Preparamos los QuerySets base
    usuarios_qs = Usuario.objects.all()
    familiares_qs = CargaFamiliar.objects.all()
    # Si hay un filtro aplicado, filtramos los QuerySets
    if consejo_seleccionado:
        # Filtramos vecinos por su consejo
        usuarios_qs = usuarios_qs.filter(consejo_comunal=consejo_seleccionado)
        # Filtramos carga familiar basándonos en el consejo del usuario (padre/tutor)
        familiares_qs = familiares_qs.filter(usuario__consejo_comunal=consejo_seleccionado)
    def clasificar(fecha_nac, genero):
        if not fecha_nac: return
        edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
        if edad <= 12: idx = 0
        elif 13 <= edad <= 17: idx = 1
        elif 18 <= edad <= 59: idx = 2
        else: idx = 3
        if genero == 'Femenino':
            fem[idx] += 1
        else:
            masc[idx] += 1
    # Procesar datos filtrados
    for u in usuarios_qs:
        clasificar(u.fecha_nacimiento, u.genero)
    for f in familiares_qs:
        clasificar(f.fecha_nacimiento, f.genero)
    context = {
        'total_vecinos': usuarios_qs.count(),
        'total_comunidad': usuarios_qs.count() + familiares_qs.count(),
        'ninos': fem[0] + masc[0],
        'adolescentes': fem[1] + masc[1],
        'adultos': fem[2] + masc[2],
        'mayores': fem[3] + masc[3],
        'total_mujeres': sum(fem),
        'total_hombres': sum(masc),
        'data_fem': fem,
        'data_masc': masc,
        'consejo_seleccionado': consejo_seleccionado, # Para mantener la opción marcada en el select
    }
    return render(request, 'gestion/estadisticas.html', context)

def exportar_estadisticas_pdf(request):
    consejo_f = request.GET.get('consejo_comunal', '')
    today = date.today()
    fem = [0, 0, 0, 0]
    masc = [0, 0, 0, 0]
    vecinos_qs = Usuario.objects.all()
    familiares_qs = CargaFamiliar.objects.all()
    if consejo_f:
        vecinos_qs = vecinos_qs.filter(consejo_comunal=consejo_f)
        familiares_qs = familiares_qs.filter(usuario__consejo_comunal=consejo_f)
    def clasificar(fecha_nac, genero):
        if not fecha_nac: return
        edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
        idx = 0 if edad <= 12 else 1 if edad <= 17 else 2 if edad <= 59 else 3
        if genero == 'Femenino': fem[idx] += 1
        else: masc[idx] += 1
    for u in vecinos_qs: clasificar(u.fecha_nacimiento, u.genero)
    for f in familiares_qs: clasificar(f.fecha_nacimiento, f.genero)
    venezuela_tz = pytz.timezone('America/Caracas')
    ahora_local = timezone.now().astimezone(venezuela_tz)
    ruta_logo_fisica = os.path.join(settings.BASE_DIR, 'gestion', 'static', 'gestion', 'Logo2.png')
    context = {
        'data_fem': fem,
        'data_masc': masc,
        'total_ninos': fem[0] + masc[0],
        'total_adol': fem[1] + masc[1],
        'total_adultos': fem[2] + masc[2],
        'total_mayores': fem[3] + masc[3],
        'total_mujeres': sum(fem),
        'total_hombres': sum(masc),
        'total_comunidad': sum(fem) + sum(masc),
        'ruta_logo': ruta_logo_fisica,
        'consejo': consejo_f,
        'fecha_emision': ahora_local.strftime('%d/%m/%Y'),
        'hora_emision': ahora_local.strftime('%I:%M %p'),
    }
    html = render_to_string('gestion/reporte_estadistico_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Reporte_Gestion_{consejo_f or "General"}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

def verificar_identidad_view(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        # Buscamos al usuario que coincida exactamente con los 3 datos
        usuario = Usuario.objects.filter(
            cedula_identidad=cedula,
            telefono=telefono,
            email=correo
        ).first()
        if usuario:
            # Guardamos el ID en la sesión para el siguiente paso
            request.session['usuario_recuperacion_id'] = usuario.id
            return redirect('restablecer_password')
        else:
            messages.error(request, "Los datos ingresados no coinciden con nuestros registros. Verifique e intente de nuevo.")
    return render(request, 'gestion/verificar_identidad.html')

def restablecer_password_view(request):
    # Verificamos que el usuario haya pasado por el paso anterior
    usuario_id = request.session.get('usuario_recuperacion_id')
    if not usuario_id:
        return redirect('verificar_identidad')
    if request.method == 'POST':
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 == pass2:
            usuario = get_object_or_404(Usuario, id=usuario_id)
            usuario.password = make_password(pass1)
            usuario.save()
            # Limpiamos la sesión de recuperación
            del request.session['usuario_recuperacion_id']
            messages.success(request, "Contraseña actualizada con éxito. Ya puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "Las contraseñas no coinciden.")
    return render(request, 'gestion/restablecer_password.html')