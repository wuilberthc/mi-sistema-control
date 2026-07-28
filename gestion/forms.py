from django import forms
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
    RegistroCompra,
    Trabajo,
    Transaccion,
)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'rif_cedula',
            'telefono',
            'direccion',
            'nota_privada',
            'foto',
            'latitud',
            'longitud',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'rif_cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. V-12345678 o J-12345678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección física'}),
            'nota_privada': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas internas u observaciones...'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.000000'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.000000'}),
        }


class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['tipo', 'concepto', 'monto', 'categoria', 'fecha', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Venta de equipos'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles adicionales...'}),
        }


class CuentaPorPagarForm(forms.ModelForm):
    class Meta:
        model = CuentaPorPagar
        fields = [
            'proveedor',
            'concepto',
            'monto_deuda',
            'monto_pagado',
            'fecha_emision',
            'fecha_vencimiento',
            'estado',
            'observaciones',
        ]
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Factura #1234'}),
            'monto_deuda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'monto_pagado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CuentaPorCobrarForm(forms.ModelForm):
    class Meta:
        model = CuentaPorCobrar
        fields = [
            'cliente',
            'concepto',
            'monto_deuda',
            'monto_cobrado',
            'fecha_emision',
            'fecha_vencimiento',
            'estado',
            'observaciones',
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Factura o Servicio'}),
            'monto_deuda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'monto_cobrado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DatosEmpresaForm(forms.ModelForm):
    class Meta:
        model = DatosEmpresa
        fields = '__all__'
        widgets = {
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'identificacion_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentaje_ganancia': forms.NumberInput(attrs={'class': 'form-control'}),
            'porcentaje_impuesto': forms.NumberInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RegistroCompraForm(forms.ModelForm):
    class Meta:
        model = RegistroCompra
        fields = '__all__'
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_comprada': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_unitario_compra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = '__all__'
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas_adicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrabajoForm(forms.ModelForm):
    class Meta:
        model = Trabajo
        fields = ['cliente', 'tecnico', 'titulo', 'descripcion', 'monto_cobrado', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tecnico': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la obra o trabajo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada...'}),
            'monto_cobrado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }


class ItemPresupuestoForm(forms.ModelForm):
    class Meta:
        model = ItemPresupuesto
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'min': '1'}),
        }


class GastoObraForm(forms.ModelForm):
    class Meta:
        model = GastoObra
        fields = ['descripcion', 'monto', 'fecha']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del gasto...'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class FotoTrabajoForm(forms.ModelForm):
    class Meta:
        model = FotoTrabajo
        fields = ['foto'] # Ajusta el campo si en tu modelo tiene otro nombre (ej. 'foto')
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }