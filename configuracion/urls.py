from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from gestion import views

urlpatterns = [
    # =========================================================================
    # 1. PANEL DE ADMINISTRACIÓN Y AUTENTICACIÓN
    # =========================================================================
    path("admin/", admin.site.urls),
    path("admin/login/", views.vista_login_personalizado, name="admin_login_custom"),
    path("login/", views.vista_login_personalizado, name="login"),

    # =========================================================================
    # 2. DASHBOARD Y TÉCNICOS
    # =========================================================================
    path("", views.dashboard_principal, name="dashboard"),
    path("mis-trabajos/", views.pantalla_tecnicos, name="pantalla_tecnicos"),
    path("tecnicos/mis-trabajos/", views.mis_trabajos, name="mis_trabajos"),

    # =========================================================================
    # 3. MÓDULO DE CLIENTES
    # =========================================================================
    path("clientes/", views.vista_lista_clientes, name="lista_clientes"),
    path("clientes/nuevo/", views.crear_cliente, name="registrar_cliente"),
    path("clientes/editar/<int:pk>/", views.modificar_cliente, name="modificar_cliente"),

    # =========================================================================
    # 4. PRODUCTOS Y PROVEEDORES
    # =========================================================================
    path("productos/", views.vista_lista_productos, name="lista_productos"),
    path("productos/nuevo/", views.registrar_producto, name="registrar_producto"),
    path("productos/editar/<int:pk>/", views.modificar_producto, name="modificar_producto"),
    path("proveedores/crear-rapido/", views.crear_proveedor_modal, name="crear_proveedor_modal"),
    path("crear-producto-modal/", views.crear_producto_modal, name="crear_producto_modal"),

    # =========================================================================
    # 5. TRABAJOS Y OBRAS
    # =========================================================================
    path("trabajos/", views.vista_lista_trabajos, name="lista_trabajos"),
    path("trabajos/nuevo/", views.crear_trabajo, name="crear_trabajo"),
    path("trabajos/detalle/<int:pk>/", views.detalle_trabajo, name="detalle_trabajo"),

    # =========================================================================
    # 6. PRESUPUESTOS Y ERP
    # =========================================================================
    path("presupuestos/", views.vista_lista_presupuestos, name="lista_presupuestos"),
    path("presupuestos/nuevo/", views.registrar_presupuesto, name="registrar_presupuesto"),
    path("presupuestos/editar/<int:pk>/", views.modificar_presupuesto, name="modificar_presupuesto"),
    path("presupuestos/eliminar/<int:pk>/", views.eliminar_presupuesto, name="eliminar_presupuesto"),
    path("presupuesto/<int:presupuesto_id>/imprimir/", views.vista_imprimir_presupuesto, name="imprimir_presupuesto"),
    path("presupuesto/<int:presupuesto_id>/aprobar-erp/", views.procesar_aprobacion_erp, name="aprobar_erp"),

    # =========================================================================
    # 7. AGENDA DE VISITAS Y CAMPO
    # =========================================================================
    path("visitas/", views.lista_visitas, name="lista_visitas"),
    path("visitas/nueva/", views.registrar_visita, name="registrar_visita"),
    path("visitas/modificar/<int:pk>/", views.modificar_visita, name="modificar_visita"),

    # =========================================================================
    # 8. ÓRDENES DE COMPRA
    # =========================================================================
    path("compras/", views.vista_lista_compras, name="lista_compras"),
    path("compras/nueva/", views.registrar_compra, name="registrar_compra"),

    # =========================================================================
    # 9. FINANZAS Y REPORTES
    # =========================================================================
    path("reporte-financiero/", views.reporte_financiero, name="reporte_financiero"),
    path("finanzas/", views.reporte_ganancias_perdidas, name="reporte_financiero_nuevo"),
    path("finanzas/nueva/", views.registrar_transaccion, name="registrar_transaccion"),

    # =========================================================================
    # 10. CUENTAS POR PAGAR Y COBRAR
    # =========================================================================
    path("cuentas-por-pagar/", views.lista_cuentas_por_pagar, name="cuentas_por_pagar"),
    path("cuentas-por-pagar/nueva/", views.registrar_cuenta_por_pagar, name="registrar_cxp"),
    path("cuentas-por-pagar/ver/<int:pk>/", views.ver_cuenta_por_pagar, name="ver_cuenta_por_pagar"),
    path("cuentas-por-pagar/editar/<int:pk>/", views.modificar_cuenta_por_pagar, name="modificar_cuenta_por_pagar"),
    
    path("cuentas-por-cobrar/", views.lista_cuentas_por_cobrar, name="lista_cuentas_por_cobrar"),
    path("cuentas-por-cobrar/nueva/", views.registrar_cuenta_por_cobrar, name="registrar_cxc"),
    path("cuentas-por-cobrar/ver/<int:pk>/", views.ver_cuenta_por_cobrar, name="ver_cuenta_por_cobrar"),
    path("cuentas-por-cobrar/editar/<int:pk>/", views.modificar_cuenta_por_cobrar, name="modificar_cuenta_por_cobrar"),

    # =========================================================================
    # 11. CONFIGURACIÓN DE LA EMPRESA
    # =========================================================================
    path("empresa/configurar/", views.editar_datos_empresa, name="datos_empresa"),

    # =========================================================================
    # 12. USUARIOS
    # =========================================================================
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
    path("usuarios/editar/<int:user_id>/", views.editar_usuario, name="editar_usuario"),
]

if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)