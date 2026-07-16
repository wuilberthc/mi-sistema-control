from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gestion import views  # Importamos las pantallas del sistema

urlpatterns = [
    # 1. PÁGINA DE INICIO PRINCIPAL (DASHBOARD PREMIUM OSCURO)
    path('', views.dashboard_principal, name='dashboard'),
    
    # INTERCEPCIÓN MÁGICA: Obliga al panel interno a usar tu login oscuro premium
    path('admin/login/', views.vista_login_personalizado, name='admin_login_custom'),
    
    # 2. MOTOR DE ADMINISTRACIÓN NATIVO DE DJANGO
    path('admin/', admin.site.urls),
    
    # 3. PANTALLA EXCLUSIVA PARA TÉCNICOS EN EL CELULAR
    path('mis-trabajos/', views.pantalla_tecnicos, name='pantalla_tecnicos'),
    
    # 4. REPORTES ADMINISTRATIVOS Y AUDITORÍA DE GANANCIAS
    path('reporte-financiero/', views.reporte_financiero, name='reporte_financiero'),
    
    # 5. IMPRENTA AUTOMÁTICA DE COTIZACIONES Y FORMATO PDF
    path('presupuesto/<int:presupuesto_id>/imprimir/', views.vista_imprimir_presupuesto, name='imprimir_presupuesto'),
    
    # 6. INICIO DE SESIÓN ESTÁNDAR VISUAL E INTUITIVO
    path('login/', views.vista_login_personalizado, name='login'),
    
    # =========================================================================
    # RUTAS DEL ENTORNO INTUITIVO PREMIUM (PANTALLAS INTERNAS PERSONALIZADAS)
    # =========================================================================
    path('clientes/', views.vista_lista_clientes, name='lista_clientes'),
    path('productos/', views.vista_lista_productos, name='lista_productos'),
    path('trabajos/', views.vista_lista_trabajos, name='lista_trabajos'),
    path('presupuestos/', views.vista_lista_presupuestos, name='lista_presupuestos'),
    path('compras/', views.vista_lista_compras, name='lista_compras'),
    
    # DISPARADOR DEL MOTOR ERP AUTOMATIZADO (DESCUENTA STOCK Y CREA OBRA)
    path('presupuesto/<int:presupuesto_id>/aprobar-erp/', views.procesar_aprobacion_erp, name='aprobar_erp'),
]

# Esto permite que Django pueda mostrar los logotipos y fotos en el navegador de forma local
if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
