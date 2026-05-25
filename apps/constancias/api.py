from ninja import Router
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render

import os
from .models import Constancia
from .schemas import ConstanciaIn, ConstanciaOut
from configuracion_comuna.auth import AuthBearer

from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
from django.template.loader import render_to_string

import base64
import datetime
import io
import locale
import os
import pytz
import qrcode

router = Router(auth=AuthBearer())

@router.post("/", response=ConstanciaOut)
def solicitar_constancia(request, data: ConstanciaIn):
    constancia = Constancia.objects.create(
        usuario=request.auth,
        anios_residencia=data.anios_residencia,
        motivo=data.motivo
    )
    return constancia

@router.get("/validar/{codigo}/", auth=None) 
def validar_constancia(request, codigo: str):
    constancia = Constancia.objects.filter(codigo=codigo, estatus='Aprobada').first()
    # Verificamos que la constancia no se encuentre vencida
    if not constancia:
        return render(request, 'validacion/validacion_erronea.html')
    elif constancia.fecha_aprobacion and (datetime.datetime.now(pytz.utc) - constancia.fecha_aprobacion).days > 30:
        return {"message": "Constancia vencida"}
    else:
        return render(request, 'validacion/validacion_exitosa.html')


@router.get("/imprimir-constancia/{constancia_id}/")
def descargar_pdf(request, constancia_id: int):
    # Solo se genera si está aprobada
    usuario = request.auth
    constancia = get_object_or_404(Constancia, pk=constancia_id, estatus='Aprobada')
    venezuela_tz = pytz.timezone('America/Caracas')
    fecha_referencia = constancia.fecha_aprobacion if constancia.fecha_aprobacion else constancia.fecha_solicitud
    fecha_local = fecha_referencia.astimezone(venezuela_tz)
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    # Creamos el contenido del QR
    scheme = request.scheme
    host = request.get_host()
    url_validacion = f"{scheme}://{host}/constancias/validar/{constancia.codigo}/"

    datos_qr = (
        url_validacion
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
        'url_validacion': url_validacion,
        'qr_code': qr_base64
    }
    html_string = render_to_string('pdf/pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Constancia_{usuario.cedula}.pdf"'
    # xhtml2pdf sabe interpretar rutas físicas de archivos si están bien formadas
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response