from django.db import models
from django.contrib.auth.models import User

# =========================================================================
# 1. CONTROL DE CLIENTES (Foto y GPS)
# =========================================================================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='clientes/', blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.nombre


# =========================================================================
# 2. PROVEEDORES Y CONTROL DE INVENTARIO
# =========================================================================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    stock_actual = models.IntegerField(default=0, verbose_name="Existencia Actual")
    stock_minimo = models.IntegerField(default=5)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ultimo Precio Costo")
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=30.0)
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=16.0)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, verbose_name="Proveedor Habitual")
    foto = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Foto del Producto")

    @property
    def necesita_compra(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def precio_venta(self):
        con_ganancia = float(self.precio_costo) * (1 + (float(self.porcentaje_ganancia) / 100))
        precio_final = con_ganancia * (1 + (float(self.porcentaje_impuesto) / 100))
        return round(precio_final, 2)

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock_actual})"


# =========================================================================
# 3. HISTORIAL DE COMPRAS (Abastecimiento de Inventario)
# =========================================================================
class RegistroCompra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compras_inventario')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    cantidad_comprada = models.IntegerField(verbose_name="Cantidad que Entra")
    costo_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Unitario de Compra")
    fecha_compra = models.DateField(verbose_name="Fecha de Factura / Compra")

    class Meta:
        verbose_name = "Control de Compra / Ingreso"
        verbose_name_plural = "Control de Compras (Ingresos)"

    def save(self, *args, **kwargs):
        es_nueva_compra = self.pk is None
        if es_nueva_compra:
            self.producto.stock_actual += int(self.cantidad_comprada)
            self.producto.precio_costo = self.costo_unitario_compra
            self.producto.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra #{self.id} - {self.cantidad_comprada} uni. de {self.producto.nombre}"


# =========================================================================
# 4. CONTROL DE TRABAJOS Y FOTOS MÚLTIPLES
# =========================================================================
class Trabajo(models.Model):
    ESTADOS = [
        ('PEND', 'Pendiente / Planificado'),
        ('PROG', 'En Progreso'),
        ('TERM', 'Terminado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tecnico Asignado")
    titulo = models.CharField(max_length=150, verbose_name="Título del Trabajo u Obra")
    descripcion = models.TextField(verbose_name="Notas / Descripción del Avance", blank=True, null=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=4, choices=ESTADOS, default='PEND')
    monto_cobrado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Cobrado al Cliente")

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre} ({self.get_estado_display()})"

class FotoTrabajo(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, related_name='fotos')
    foto = models.ImageField(upload_to='trabajos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.trabajo.titulo}"


# =========================================================================
# 5. CONTROL DE GASTOS DE LA OBRA
# =========================================================================
class GastoObra(models.Model):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, related_name='gastos', verbose_name="Obra / Trabajo")
    descripcion = models.CharField(max_length=200, verbose_name="Concepto del Gasto (Ej. Transporte, Almuerzos)")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.descripcion} - ${self.monto} ({self.trabajo.titulo})"


# =========================================================================
# 6. CONFIGURACIÓN DEL ENCABEZADO DE LA EMPRESA
# =========================================================================
class DatosEmpresa(models.Model):
    nombre_comercial = models.CharField(max_length=150, verbose_name="Nombre de la Empresa")
    identificacion_fiscal = models.CharField(max_length=50, verbose_name="RIF / NIT / RUT")
    telefono = models.CharField(max_length=50, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='empresa/', blank=True, null=True, verbose_name="Logotipo de la Empresa")

    class Meta:
        verbose_name = "Datos de mi Empresa"
        verbose_name_plural = "Datos de mi Empresa"

    def __str__(self):
        return self.nombre_comercial


# =========================================================================
# 7. SISTEMA DE PRESUPUESTOS AUTOMATIZADOS (Neto e IVA)
# =========================================================================
class Presupuesto(models.Model):
    ESTADOS = [
        ('BORR', 'Borrador'),
        ('ENVI', 'Enviado al Cliente'),
        ('ACEP', 'Aceptado (Crear Obra)'),
        ('RECH', 'Rechazado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=4, choices=ESTADOS, default='BORR')
    notas_adicionales = models.TextField(blank=True, null=True, verbose_name="Condiciones o Notas del Presupuesto")

    @property
    def total_presupuesto(self):
        total = sum(float(item.producto.precio_venta) * int(item.cantidad) for item in self.items.all())
        return round(total, 2)

    def __str__(self):
        return f"Presupuesto #{self.id} - {self.cliente.nombre} (${self.total_presupuesto})"

class ItemPresupuesto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Material / Servicio")
    cantidad = models.IntegerField(default=1)

    @property
    def subtotal(self):
        precio_venta_producto = float(self.producto.precio_venta)
        cantidad_solicitada = int(self.cantidad)
        subtotal_neto_renglon = (precio_venta_producto * cantidad_solicitada) / 1.16
        return round(subtotal_neto_renglon, 2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
