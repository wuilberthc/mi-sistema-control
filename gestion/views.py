from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Sum
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import (
    ClienteForm,
    CuentaPorCobrarForm,
    CuentaPorPagarForm,
    DatosEmpresaForm,
    FotoTrabajoForm,
    GastoObraForm,
    ItemPresupuestoForm,
    PresupuestoForm,
    ProductoForm,
    RegistroCompraForm,
    TrabajoForm,
    TransaccionForm,
    VisitaCampoForm,
)
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
    VisitaCampo,
)


# =========================================================================
# 1. PÁGINA DE INICIO PRINCIPAL (DASHBOARD VISUAL MODERNO)
# =========================================================================

def dashboard_principal(request):
    context = {
        'clientes': Cliente.objects.count(),
        'progreso': Trabajo.objects.filter(estado='PROG').count(),
        'terminadas': Trabajo.objects.filter(estado='TERM').count(),
        'presupuestos': Presupuesto.objects.filter(estado='BORR').count(),
        'alerta_stock': Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count(),
        'visitas_pendientes': VisitaCampo.objects.filter(estado='PEND').count(),
    }
    return render(request, 'gestion/dashboard.html', context)


# =========================================================================
# 2. PANTALLA EXCLUSIVA PARA TÉCNICOS EN EL CELULAR
# =========================================================================

@login_required(login_url='/login/')
def pantalla_tecnicos(request):
    if request.method == 'POST':
        trabajo_id = request.POST.get('trabajo_id')
        imagenes = request.FILES.getlist('fotos_nuevas')
        notas = request.POST.get('notas')
        nuevo_estado = request.POST.get('estado')

        if trabajo_id:
            trabajo = get_object_or_404(Trabajo, id=trabajo_id, tecnico=request.user)

            if notas:
                if trabajo.descripcion:
                    trabajo.descripcion += f'\n\n--- Actualizacion ---\n{notas}'
                else:
                    trabajo.descripcion = notas

            if nuevo_estado:
                trabajo.estado = nuevo_estado

            trabajo.save()

            for img in imagenes:
                FotoTrabajo.objects.create(trabajo=trabajo, foto=img)

            return redirect('pantalla_tecnicos')

    trabajos = Trabajo.objects.filter(tecnico=request.user).order_by('-id')
    return render(request, 'gestion/tecnicos.html', {'trabajos': trabajos})


@login_required(login_url='/login/')
def mis_trabajos(request):
    trabajos = Trabajo.objects.filter(tecnico=request.user).order_by('-id')
    return render(request, 'gestion/tecnicos.html', {'trabajos': trabajos})


# =========================================================================
# 3. PANEL ADMINISTRATIVO - REPORTE FINANCIERO DE OBRAS
# =========================================================================

def reporte_financiero(request):
    cliente_filtrado = request.GET.get('filtro_cliente')
    estado_filtrado = request.GET.get('filtro_estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    trabajos = Trabajo.objects.all().order_by('-id')

    if cliente_filtrado:
        trabajos = trabajos.filter(cliente_id=cliente_filtrado)
    if estado_filtrado:
        trabajos = trabajos.filter(estado=estado_filtrado)

    if fecha_desde and fecha_hasta:
        trabajos = trabajos.filter(fecha_inicio__range=[fecha_desde, fecha_hasta])
    elif fecha_desde:
        trabajos = trabajos.filter(fecha_inicio__gte=fecha_desde)
    elif fecha_hasta:
        trabajos = trabajos.filter(fecha_inicio__lte=fecha_hasta)

    datos_reporte = []
    for trabajo in trabajos:
        total_gastos_campo = trabajo.gastos.aggregate(total=Sum('monto'))['total'] or 0
        monto_cobrado = trabajo.monto_cobrado
        ganancia_neta = float(monto_cobrado) - float(total_gastos_campo)

        datos_reporte.append({
            'trabajo': trabajo,
            'monto_cobrado': monto_cobrado,
            'gastos_campo': total_gastos_campo,
            'ganancia_neta': round(ganancia_neta, 2),
        })

    context = {
        'reportes': datos_reporte,
        'clientes': Cliente.objects.all().order_by('nombre'),
        'cliente_sel': cliente_filtrado,
        'estado_sel': estado_filtrado,
        'fecha_desde_sel': fecha_desde,
        'fecha_hasta_sel': fecha_hasta,
    }
    return render(request, 'gestion/reporte_financiero.html', context)


# =========================================================================
# 4. VISTA DE IMPRESIÓN - DESGLOSE AUTOMÁTICO DE SUB-TOTAL E IVA (16%)
# =========================================================================

def vista_imprimir_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    empresa = DatosEmpresa.objects.first()

    if hasattr(presupuesto, 'items') and presupuesto.items.exists():
        items_base = presupuesto.items.all()
    elif hasattr(presupuesto, 'itempresupuesto_set') and presupuesto.itempresupuesto_set.exists():
        items_base = presupuesto.itempresupuesto_set.all()
    else:
        items_base = ItemPresupuesto.objects.filter(presupuesto=presupuesto)

    items_calculados = []
    for item in items_base:
        subtotal_item = float(item.subtotal) if hasattr(item, 'subtotal') else 0.0
        cantidad = int(item.cantidad) if hasattr(item, 'cantidad') else 1
        precio_unitario_neto = subtotal_item / cantidad if cantidad > 0 else 0

        items_calculados.append({
            'nombre': item.producto.nombre if hasattr(item, 'producto') and item.producto else 'Ítems diversos',
            'cantidad': cantidad,
            'precio_unitario': round(precio_unitario_neto, 2),
            'subtotal': round(subtotal_item, 2),
        })

    total_general = float(presupuesto.total_presupuesto) if hasattr(presupuesto, 'total_presupuesto') else 0.0
    subtotal_final = total_general / 1.16
    iva_final = subtotal_final * 0.16

    context = {
        'presupuesto': presupuesto,
        'empresa': empresa,
        'items_finales': items_calculados,
        'subtotal': round(subtotal_final, 2),
        'iva': round(iva_final, 2),
        'total': round(total_general, 2),
    }
    return render(request, 'gestion/imprimir_presupuesto.html', context)


# =========================================================================
# 5. LISTADOS GENERALES
# =========================================================================

def vista_lista_clientes(request):
    return render(request, 'gestion/lista_clientes.html', {'lista_clientes': Cliente.objects.all().order_by('nombre')})


def vista_lista_productos(request):
    return render(request, 'gestion/lista_productos.html', {'lista_productos': Producto.objects.all().order_by('nombre')})


def vista_lista_trabajos(request):
    return render(request, 'gestion/lista_trabajos.html', {'lista_trabajos': Trabajo.objects.all().order_by('-id')})


def vista_lista_presupuestos(request):
    return render(request, 'gestion/lista_presupuestos.html', {'lista_presupuestos': Presupuesto.objects.all().order_by('-id')})


def vista_lista_compras(request):
    return render(request, 'gestion/lista_compras.html', {'lista_compras': RegistroCompra.objects.all().order_by('-id')})


# =========================================================================
# 6. MOTOR CORE ERP: TRANSFORMAR PRESUPUESTO EN OBRA Y DESCONTAR ALMACÉN
# =========================================================================

def procesar_aprobacion_erp(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)

    if presupuesto.estado == 'ACEP':
        return redirect('lista_presupuestos')

    items_presupuesto = (
        presupuesto.items.all()
        if hasattr(presupuesto, 'items') and presupuesto.items.exists()
        else presupuesto.itempresupuesto_set.all()
    )

    for item in items_presupuesto:
        producto_inventario = item.producto
        producto_inventario.stock_actual -= int(item.cantidad)
        producto_inventario.save()

    descripcion_items = '\n'.join([f'- {i.cantidad}x {i.producto.nombre}' for i in items_presupuesto])
    notas_adicionales = presupuesto.notas_adicionales or 'Sin notas.'

    Trabajo.objects.create(
        cliente=presupuesto.cliente,
        titulo=f'OBRA: {presupuesto.cliente.nombre} (Presupuesto #{presupuesto.id})',
        descripcion=f'Actividades / Materiales instalados:\n{descripcion_items}\n\nNotas:\n{notas_adicionales}',
        monto_cobrado=presupuesto.total_presupuesto,
        estado='PEND',
    )

    presupuesto.estado = 'ACEP'
    presupuesto.save()

    return redirect('lista_trabajos')


# =========================================================================
# 7. AUTENTICACIÓN (LOGIN PERSONALIZADO)
# =========================================================================

def vista_login_personalizado(request):
    error = False
    if request.method == 'POST':
        usuario = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')
        error = True

    return render(request, 'gestion/login.html', {'error_login': error})


# =========================================================================
# 8. REPORTE DE GANANCIAS Y PÉRDIDAS (FINANZAS)
# =========================================================================

def reporte_ganancias_perdidas(request):
    total_ingresos = Transaccion.objects.filter(tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = Transaccion.objects.filter(tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
    
    context = {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'utilidad_neta': total_ingresos - total_gastos,
        'transacciones': Transaccion.objects.all().order_by('-fecha'),
    }
    return render(request, 'gestion/reporte_financiero.html', context)


def registrar_transaccion(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reporte_financiero')
    else:
        form = TransaccionForm()

    return render(request, 'gestion/registrar_transaccion.html', {'form': form})


# =========================================================================
# 9. MÓDULO DE CUENTAS POR PAGAR
# =========================================================================

def lista_cuentas_por_pagar(request):
    cuentas = CuentaPorPagar.objects.all().order_by('fecha_vencimiento')
    
    total_deuda_pendiente = sum(
        (c.monto_deuda - c.monto_pagado) for c in cuentas if c.estado != 'PAG'
    )

    context = {
        'cuentas': cuentas,
        'total_deuda_pendiente': total_deuda_pendiente,
    }
    return render(request, 'gestion/lista_cuentas_por_pagar.html', context)


def registrar_cuenta_por_pagar(request):
    if request.method == 'POST':
        form = CuentaPorPagarForm(request.POST)
        if form.is_valid():
            cuenta = form.save()
            if cuenta.monto_pagado > 0:
                Transaccion.objects.create(
                    tipo='gasto',
                    monto=cuenta.monto_pagado,
                    descripcion=f'Pago CxP Proveedor: {cuenta.proveedor if hasattr(cuenta, "proveedor") else "General"} - Concepto: {cuenta.concepto}',
                    fecha=date.today()
                )
                if cuenta.monto_pagado >= cuenta.monto_deuda:
                    cuenta.estado = 'PAG'
                    cuenta.save()
            return redirect('cuentas_por_pagar')
    else:
        form = CuentaPorPagarForm()

    return render(request, 'gestion/registrar_cxp.html', {'form': form})


def ver_cuenta_por_pagar(request, pk):
    cuenta = get_object_or_404(CuentaPorPagar, pk=pk)
    return render(request, 'gestion/ver_cuenta_por_pagar.html', {'cuenta': cuenta})


def modificar_cuenta_por_pagar(request, pk):
    cuenta = get_object_or_404(CuentaPorPagar, pk=pk)
    monto_pagado_anterior = float(cuenta.monto_pagado)

    if request.method == 'POST':
        form = CuentaPorPagarForm(request.POST, instance=cuenta)
        if form.is_valid():
            cuenta_actualizada = form.save()

            diferencia_pago = float(cuenta_actualizada.monto_pagado) - monto_pagado_anterior
            if diferencia_pago > 0:
                Transaccion.objects.create(
                    tipo='gasto',
                    monto=diferencia_pago,
                    descripcion=f'Abono/Pago CxP: {cuenta_actualizada.concepto}',
                    fecha=date.today()
                )

            return redirect('cuentas_por_pagar')
    else:
        form = CuentaPorPagarForm(instance=cuenta)
    
    return render(request, 'gestion/modificar_cuenta_por_pagar.html', {'form': form, 'cuenta': cuenta})


# =========================================================================
# 10. MÓDULO DE CUENTAS POR COBRAR
# =========================================================================

def lista_cuentas_por_cobrar(request):
    return render(request, 'gestion/lista_cuentas_por_cobrar.html', {'cuentas': CuentaPorCobrar.objects.all().order_by('fecha_vencimiento')})


def registrar_cuenta_por_cobrar(request):
    if request.method == 'POST':
        form = CuentaPorCobrarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_cuentas_por_cobrar')
    else:
        form = CuentaPorCobrarForm()

    return render(request, 'gestion/registrar_cxc.html', {'form': form})


def ver_cuenta_por_cobrar(request, pk):
    cuenta = get_object_or_404(CuentaPorCobrar, pk=pk)
    return render(request, 'gestion/ver_cuenta_por_cobrar.html', {'cuenta': cuenta})


def modificar_cuenta_por_cobrar(request, pk):
    cuenta = get_object_or_404(CuentaPorCobrar, pk=pk)
    if request.method == 'POST':
        form = CuentaPorCobrarForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            return redirect('lista_cuentas_por_cobrar')
    else:
        form = CuentaPorCobrarForm(instance=cuenta)
    
    return render(request, 'gestion/modificar_cuenta_por_cobrar.html', {'form': form, 'cuenta': cuenta})


# =========================================================================
# 11. REGISTRO Y MODIFICACIÓN DE CLIENTES, PRODUCTOS, COMPRAS Y CONFIGURACIÓN
# =========================================================================

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'gestion/registrar_cliente.html', {'form': form})


def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'gestion/crear_cliente.html', {'form': form})


def modificar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'gestion/modificar_cliente.html', {'form': form, 'cliente': cliente})


def registrar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()

    return render(request, 'gestion/registrar_producto.html', {'form': form})


def modificar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'gestion/editar_producto.html', {'form': form, 'producto': producto})


def registrar_compra(request):
    if request.method == 'POST':
        form = RegistroCompraForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_compras')
    else:
        form = RegistroCompraForm()

    return render(request, 'gestion/registrar_compra.html', {'form': form})


def editar_datos_empresa(request):
    empresa = DatosEmpresa.objects.first()

    if request.method == 'POST':
        form = DatosEmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DatosEmpresaForm(instance=empresa)

    return render(request, 'gestion/datos_empresa.html', {'form': form})


# =========================================================================
# 12. REGISTRO Y MODIFICACIÓN DE PRESUPUESTOS (CON SOPORTE INLINE DE ÍTEMS)
# =========================================================================

def registrar_presupuesto(request):
    ItemPresupuestoFormSet = inlineformset_factory(
        Presupuesto, 
        ItemPresupuesto, 
        form=ItemPresupuestoForm, 
        extra=5, 
        can_delete=True
    )

    if request.method == 'POST':
        form = PresupuestoForm(request.POST, request.FILES)
        formset = ItemPresupuestoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            presupuesto = form.save()
            formset.instance = presupuesto
            formset.save()
            return redirect('lista_presupuestos')
    else:
        form = PresupuestoForm()
        formset = ItemPresupuestoFormSet()

    return render(request, 'gestion/registrar_presupuesto.html', {
        'form': form,
        'inline_formset': formset,
        'editando': False
    })


def modificar_presupuesto(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    
    ItemPresupuestoFormSet = inlineformset_factory(
        Presupuesto, 
        ItemPresupuesto, 
        form=ItemPresupuestoForm, 
        extra=5, 
        can_delete=True
    )

    if request.method == 'POST':
        form = PresupuestoForm(request.POST, request.FILES, instance=presupuesto)
        formset = ItemPresupuestoFormSet(request.POST, instance=presupuesto)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('lista_presupuestos')
    else:
        form = PresupuestoForm(instance=presupuesto)
        formset = ItemPresupuestoFormSet(instance=presupuesto)

    return render(request, 'gestion/registrar_presupuesto.html', {
        'form': form,
        'inline_formset': formset,
        'presupuesto': presupuesto,
        'editando': True
    })


def eliminar_presupuesto(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    presupuesto.delete()
    messages.success(request, f"El presupuesto #{pk} ha sido eliminado correctamente.")
    return redirect('lista_presupuestos')


# =========================================================================
# 13. REGISTRO RÁPIDO DE PROVEEDOR Y PRODUCTO (MODAL FRONTEND)
# =========================================================================

def crear_proveedor_modal(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        if nombre:
            Proveedor.objects.create(nombre=nombre, telefono=telefono)
        return redirect(request.META.get("HTTP_REFERER", "registrar_producto"))
    return redirect("registrar_producto")


def crear_producto_modal(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        stock_actual = request.POST.get('stock_actual', 0)
        stock_minimo = request.POST.get('stock_minimo', 1)
        precio_costo = request.POST.get('precio_costo', 0)
        porcentaje_ganancia = request.POST.get('porcentaje_ganancia', 30)

        if nombre:
            producto = Producto.objects.create(
                nombre=nombre,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                precio_costo=precio_costo,
                porcentaje_ganancia=porcentaje_ganancia
            )
            return JsonResponse({
                'status': 'success',
                'id': producto.id,
                'nombre': producto.nombre
            })
    return JsonResponse({'status': 'error'}, status=400)


# =========================================================================
# 14. REGISTRO DE TRABAJOS Y GESTIÓN DETALLADA DE OBRAS / GASTOS
# =========================================================================

def crear_trabajo(request):
    if request.method == 'POST':
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_trabajos')
    else:
        form = TrabajoForm()
     
    return render(request, 'gestion/registrar_trabajo.html', {'form': form})


def detalle_trabajo(request, pk):
    trabajo = get_object_or_404(Trabajo, pk=pk)
    gastos = GastoObra.objects.filter(trabajo=trabajo)
    fotos = FotoTrabajo.objects.filter(trabajo=trabajo)

    form_gasto = GastoObraForm()
    form_foto = FotoTrabajoForm()

    if request.method == 'POST':
        if 'registrar_gasto' in request.POST:
            form_gasto = GastoObraForm(request.POST)
            if form_gasto.is_valid():
                gasto = form_gasto.save(commit=False)
                gasto.trabajo = trabajo
                gasto.save()
                return redirect('detalle_trabajo', pk=trabajo.pk)
                
        elif 'registrar_foto' in request.POST:
            form_foto = FotoTrabajoForm(request.POST, request.FILES)
            if form_foto.is_valid():
                foto = form_foto.save(commit=False)
                foto.trabajo = trabajo
                foto.save()
                return redirect('detalle_trabajo', pk=trabajo.pk)

    context = {
        'trabajo': trabajo,
        'gastos': gastos,
        'fotos': fotos,
        'form_gasto': form_gasto,
        'form_foto': form_foto,
    }
    return render(request, 'gestion/detalle_trabajo.html', context)


# =========================================================================
# 15. GESTIÓN DE USUARIOS Y NIVELES
# =========================================================================

def lista_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'gestion/lista_usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo_usuario')

        if username and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            if tipo_usuario == 'admin':
                user.is_superuser = True
                user.is_staff = True
                user.save()
            return redirect('lista_usuarios')
            
    return render(request, 'gestion/form_usuario.html')

def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        usuario.username = request.POST.get('username', usuario.username)
        usuario.email = request.POST.get('email', usuario.email)
        
        password = request.POST.get('password')
        if password:
            usuario.set_password(password)
            
        tipo_usuario = request.POST.get('tipo_usuario')
        if tipo_usuario == 'admin':
            usuario.is_superuser = True
            usuario.is_staff = True
        else:
            usuario.is_superuser = False
            usuario.is_staff = False
            
        usuario.save()
        return redirect('lista_usuarios')

    return render(request, 'gestion/form_usuario.html', {'usuario': usuario})


# =========================================================================
# 16. AGENDA DE VISITAS Y TRABAJOS EN CAMPO (VISTAS)
# =========================================================================

def lista_visitas(request):
    estado_filtro = request.GET.get('estado')
    tipo_filtro = request.GET.get('tipo')
    
    visitas = VisitaCampo.objects.all().order_by('-fecha_programada')
    if estado_filtro:
        visitas = visitas.filter(estado=estado_filtro)
    if tipo_filtro:
        visitas = visitas.filter(tipo=tipo_filtro)

    context = {
        'lista_visitas': visitas,
        'estado_sel': estado_filtro,
        'tipo_sel': tipo_filtro,
    }
    return render(request, 'gestion/lista_visitas.html', context)


def registrar_visita(request):
    if request.method == 'POST':
        form = VisitaCampoForm(request.POST)
        if form.is_valid():
            visita = form.save()
            # Si la visita cobrada genera algún ingreso inmediato, se puede registrar transacción opcionalmente
            if visita.tipo == 'COBRADA' and visita.monto_cobro > 0:
                Transaccion.objects.create(
                    tipo='ingreso',
                    concepto=f'Cobro de Visita Técnica #{visita.id} - {visita.cliente.nombre}',
                    monto=visita.monto_cobro,
                    categoria='Visitas Técnicas',
                    fecha=date.today()
                )
            return redirect('lista_visitas')
    else:
        form = VisitaCampoForm()

    return render(request, 'gestion/registrar_visita.html', {'form': form})


def modificar_visita(request, pk):
    visita = get_object_or_404(VisitaCampo, pk=pk)
    if request.method == 'POST':
        form = VisitaCampoForm(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            return redirect('lista_visitas')
    else:
        form = VisitaCampoForm(instance=visita)

    return render(request, 'gestion/modificar_visita.html', {'form': form, 'visita': visita})