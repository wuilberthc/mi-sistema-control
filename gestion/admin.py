from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Proveedor, Producto, Trabajo, FotoTrabajo, GastoObra, DatosEmpresa, Presupuesto, ItemPresupuesto, RegistroCompra

# =========================================================================
# 1. CONTROL DE INVENTARIO Y REGISTRO DE COMPRAS
# =========================================================================
class RegistroCompraInline(admin.TabularInline):
    model = RegistroCompra
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('mostrar_miniatura', 'nombre', 'stock_actual', 'stock_minimo', 'precio_costo', 'precio_venta', 'alerta_stock')
    list_filter = ('proveedor',)
    search_fields = ('nombre',)
    inlines = [RegistroCompraInline]

    def mostrar_miniatura(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: contain; border-radius: 4px;" />', obj.foto.url)
        return "Sin Foto"
    mostrar_miniatura.short_description = "Imagen"

    def alerta_stock(self, obj):
        if obj.necesita_compra:
            return "COMPRAR URGENTE"
        return "Stock OK"
    alerta_stock.short_description = "Estado de Inventario"


# =========================================================================
# 2. CONTROL DE TRABAJOS, FOTOS Y GASTOS DE OBRA
# =========================================================================
class FotoTrabajoInline(admin.TabularInline):
    model = FotoTrabajo
    extra = 3

class GastoObraInline(admin.TabularInline):
    model = GastoObra
    extra = 1

@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'tecnico', 'estado', 'monto_cobrado', 'fecha_inicio')
    list_filter = ('estado', 'cliente', 'tecnico')
    search_fields = ('titulo', 'descripcion')
    inlines = [FotoTrabajoInline, GastoObraInline]


# =========================================================================
# 3. CONTROL DE CLIENTES POR PLANTILLA (MAPA GPS)
# =========================================================================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'latitud', 'longitud')
    search_fields = ('nombre',)
    change_form_template = 'gestion/mapa_cliente.html'
    fields = ('nombre', 'telefono', 'foto', ('latitud', 'longitud'))


# =========================================================================
# 4. SISTEMA DE PRESUPUESTOS CON BOTÓN DE IMPRESIÓN PDF
# =========================================================================
class ItemPresupuestoInline(admin.TabularInline):
    model = ItemPresupuesto
    extra = 2

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'estado', 'obtener_total', 'boton_imprimir')
    list_filter = ('estado', 'cliente')
    search_fields = ('cliente__nombre',)
    inlines = [ItemPresupuestoInline]

    def obtener_total(self, obj):
        return f"${obj.total_presupuesto}"
    obtener_total.short_description = "Total Presupuestado"

    def boton_imprimir(self, obj):
        return format_html(
            '<a class="button" href="/presupuesto/{}/imprimir/" target="_blank" style="background-color: #007bff; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; text-decoration: none;">🖨️ Imprimir PDF</a>',
            obj.id
        )
    boton_imprimir.short_description = "Accion"


# =========================================================================
# 5. REGISTROS COMPLEMENTARIOS SIMPLES
# =========================================================================
admin.site.register(Proveedor)
admin.site.register(DatosEmpresa)
admin.site.register(RegistroCompra)
