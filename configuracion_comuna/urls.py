from django.contrib import admin
from django.urls import path
from gestion import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/editar/<int:pk>/', views.editar_usuario_view, name='editar_usuario'),
    path('solicitar-constancia/', views.solicitar_constancia_view, name='solicitar_constancia'),
    path('registrar-carga/', views.registrar_carga_view, name='registrar_carga'),
    path('editar-carga/<int:pk>/', views.editar_carga_view, name='editar_carga'),
    path('eliminar-carga/<int:pk>/', views.eliminar_carga_view, name='eliminar_carga'),
    path('validar-constancias/', views.validar_constancias_view, name='validar_constancias'),
    path('cambiar-estatus/<int:pk>/<str:nuevo_estatus>/', views.cambiar_estatus_constancia, name='cambiar_estatus'),
    path('imprimir-constancia/<int:pk>/', views.generar_pdf_constancia, name='imprimir_constancia'),
    path('vecinos/', views.lista_vecinos_view, name='lista_vecinos'),
    path('estadisticas/', views.panel_estadisticas_view, name='panel_estadisticas'),
    path('exportar-estadisticas/', views.exportar_estadisticas_pdf, name='exportar_estadisticas_pdf'),
    path('recuperar-cuenta/', views.verificar_identidad_view, name='verificar_identidad'),
    path('restablecer-password/', views.restablecer_password_view, name='restablecer_password'),
]