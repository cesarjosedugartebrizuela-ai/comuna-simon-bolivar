from django.shortcuts import render
from .models import Constancia
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

import base64, io, os, qrcode, pytz, locale

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass

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