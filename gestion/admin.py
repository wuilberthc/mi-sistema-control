from django.contrib import admin
from .models import (
    Cliente,
    CuentaPorCobrar,
    CuentaPorPagar,
    DatosEmpresa,
    FotoTrabajo,
    GastoObra,
    ItemPresupuesto,
    Presupuesto,
    Producto,
    Proveedor,
    RegistroCompra,
    Trabajo,
    Transaccion,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rif_cedula", "telefono")
    search_fields = ("nombre", "rif_cedula")
    change_form_template = "gestion/mapa_cliente.html"


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "stock_actual",
        "precio_costo",
        "porcentaje_ganancia",
        "proveedor",
    )
    search_fields = ("nombre",)
    list_filter = ("proveedor",)


@admin.register(RegistroCompra)
class RegistroCompraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "producto",
        "proveedor",
        "cantidad_comprada",
        "costo_unitario_compra",
        "fecha_compra",
    )
    list_filter = ("proveedor", "fecha_compra")


# Inlines para la sección de Trabajos
class GastoObraInline(admin.TabularInline):
    model = GastoObra
    extra = 1


class FotoTrabajoInline(admin.TabularInline):
    model = FotoTrabajo
    extra = 1


@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "cliente", "tecnico", "estado", "monto_cobrado")
    list_filter = ("estado", "tecnico")
    search_fields = ("titulo", "cliente__nombre")
    inlines = [GastoObraInline, FotoTrabajoInline]


@admin.register(FotoTrabajo)
class FotoTrabajoAdmin(admin.ModelAdmin):
    list_display = ("id", "trabajo", "fecha_subida")


@admin.register(GastoObra)
class GastoObraAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "trabajo", "monto", "fecha")
    list_filter = ("fecha",)


@admin.register(DatosEmpresa)
class DatosEmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre_comercial", "identificacion_fiscal", "telefono")


class ItemPresupuestoInline(admin.TabularInline):
    model = ItemPresupuesto
    extra = 1


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "fecha_creacion",
        "estado",
        "total_presupuesto",
    )
    list_filter = ("estado", "fecha_creacion")
    search_fields = ("cliente__nombre",)
    inlines = [ItemPresupuestoInline]


@admin.register(CuentaPorCobrar)
class CuentaPorCobrarAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "concepto",
        "monto_deuda",
        "monto_cobrado",
        "fecha_vencimiento",
        "estado",
    )
    list_filter = ("estado", "fecha_vencimiento")
    search_fields = ("cliente__nombre", "concepto")


@admin.register(CuentaPorPagar)
class CuentaPorPagarAdmin(admin.ModelAdmin):
    list_display = (
        "proveedor",
        "concepto",
        "monto_deuda",
        "monto_pagado",
        "fecha_vencimiento",
        "estado",
    )
    list_filter = ("estado", "fecha_vencimiento")
    search_fields = ("proveedor__nombre", "concepto")


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "concepto", "monto", "categoria", "fecha")
    list_filter = ("tipo", "categoria", "fecha")
    search_fields = ("concepto", "categoria")