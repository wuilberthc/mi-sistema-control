from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from .models import Trabajo, FotoTrabajo, Presupuesto, DatosEmpresa, Cliente, Producto

# =========================================================================
# 1. PÁGINA DE INICIO PRINCIPAL (DASHBOARD VISUAL MODERNO)
# =========================================================================
def dashboard_principal(request):
    total_clientes = Cliente.objects.count()
    obras_en_progreso = Trabajo.objects.filter(estado='PROG').count()
    obras_terminadas = Trabajo.objects.filter(estado='TERM').count()
    presupuestos_pendientes = Presupuesto.objects.filter(estado='BORR').count()
    
    # Filtro automatico comparando stock actual con el minimo
    productos_sin_stock = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()

    return render(request, 'gestion/dashboard.html', {
        'clientes': total_clientes,
        'progreso': obras_en_progreso,
        'terminadas': obras_terminadas,
        'presupuestos': presupuestos_pendientes,
        'alerta_stock': productos_sin_stock
    })


# =========================================================================
# 2. PANTALLA EXCLUSIVA PARA TÉCNICOS EN EL CELULAR
# =========================================================================
@login_required(login_url='/login/') # <-- CAMBIADO: Quitamos el camino /admin/
def pantalla_tecnicos(request):
    trabajos = Trabajo.objects.filter(tecnico=request.user).order_by('-id')

    if request.method == 'POST':
        trabajo_id = request.POST.get('trabajo_id')
        imagenes = request.FILES.getlist('fotos_nuevas')
        notas = request.POST.get('notas')
        nuevo_estado = request.POST.get('estado')

        if trabajo_id:
            trabajo = Trabajo.objects.get(id=trabajo_id, tecnico=request.user)
            
            if notas:
                if trabajo.descripcion:
                    trabajo.descripcion += f"\n\n--- Actualizacion ---\n{notas}"
                else:
                    trabajo.descripcion = notas
            
            if nuevo_estado:
                trabajo.estado = nuevo_estado
            
            trabajo.save()

            for img in imagenes:
                FotoTrabajo.objects.create(trabajo=trabajo, foto=img)
                
            return redirect('pantalla_tecnicos')

    return render(request, 'gestion/tecnicos.html', {'trabajos': trabajos})


# =========================================================================
# 3. PANEL ADMINISTRATIVO - REPORTE FINANCIERO DE OBRAS
# =========================================================================
def reporte_financiero(request):
    # 1. Traemos la lista de clientes para la caja desplegable
    todos_los_clientes = Cliente.objects.all().order_by('nombre')
    
    # 2. Capturamos todos los filtros de la pantalla (Clientes, Estados y Fechas)
    cliente_filtrado = request.GET.get('filtro_cliente')
    estado_filtrado = request.GET.get('filtro_estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # 3. Base inicial: traer todas las obras
    trabajos = Trabajo.objects.all().order_by('-id')

    # 4. APLICACIÓN DE FILTROS DINÁMICOS
    if cliente_filtrado:
        trabajos = trabajos.filter(cliente_id=cliente_filtrado)
    if estado_filtrado:
        trabajos = trabajos.filter(estado=estado_filtrado)
        
    # FILTRO DE FECHAS INTELIGENTE: Valida que el usuario haya ingresado ambas fechas
    if fecha_desde and fecha_hasta:
        trabajos = trabajos.filter(fecha_inicio__range=[fecha_desde, fecha_hasta])
    elif fecha_desde:
        trabajos = trabajos.filter(fecha_inicio__gte=fecha_desde)
    elif fecha_hasta:
        trabajos = trabajos.filter(fecha_inicio__lte=fecha_hasta)

    # 5. Procesamos la matemática financiera para las obras resultantes
    datos_reporte = []
    for trabajo in trabajos:
        total_gastos_campo = trabajo.gastos.aggregate(total=Sum('monto'))['total'] or 0
        monto_cobrado = trabajo.monto_cobrado
        ganancia_neta = float(monto_cobrado) - float(total_gastos_campo)

        datos_reporte.append({
            'trabajo': trabajo,
            'monto_cobrado': monto_cobrado,
            'gastos_campo': total_gastos_campo,
            'ganancia_neta': round(ganancia_neta, 2)
        })

    # 6. Enviamos los datos de vuelta para mantener los valores fijos en la pantalla al filtrar
    return render(request, 'gestion/reporte_financiero.html', {
        'reportes': datos_reporte,
        'clientes': todos_los_clientes,
        'cliente_sel': cliente_filtrado,
        'estado_sel': estado_filtrado,
        'fecha_desde_sel': fecha_desde,
        'fecha_hasta_sel': fecha_hasta
    })

# =========================================================================
# 4. VISTA DE IMPRESIÓN - DESGLOSE AUTOMÁTICO DE SUB-TOTAL E IVA (16%)
# =========================================================================
def vista_imprimir_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    empresa = DatosEmpresa.objects.first()
    
    if presupuesto.items.exists():
        items_base = presupuesto.items.all()
    else:
        items_base = presupuesto.itempresupuesto_set.all()
    
    items_calculados = []
    for item in items_base:
        subtotal_item = float(item.subtotal)
        cantidad = int(item.cantidad)
        
        precio_unitario_neto = subtotal_item / cantidad if cantidad > 0 else 0
        
        items_calculados.append({
            'nombre': item.producto.nombre,
            'cantidad': cantidad,
            'precio_unitario': round(precio_unitario_neto, 2),
            'subtotal': round(subtotal_item, 2)
        })

    total_general = float(presupuesto.total_presupuesto)
    subtotal_final = total_general / 1.16
    iva_final = subtotal_final * 0.16
    
    return render(request, 'gestion/imprimir_presupuesto.html', {
        'presupuesto': presupuesto,
        'empresa': empresa,
        'items_finales': items_calculados,
        'subtotal': round(subtotal_final, 2),
        'iva': round(iva_final, 2),
        'total': round(total_general, 2)
    })
def vista_lista_clientes(request):
    # Buscamos todos los clientes ordenados por orden alfabetico
    todos_los_clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'gestion/lista_clientes.html', {'lista_clientes': todos_los_clientes})
def vista_lista_productos(request):
    todos_los_productos = Producto.objects.all().order_by('nombre')
    return render(request, 'gestion/lista_productos.html', {'lista_productos': todos_los_productos})
def vista_lista_trabajos(request):
    todas_las_obras = Trabajo.objects.all().order_by('-id')
    return render(request, 'gestion/lista_trabajos.html', {'lista_trabajos': todas_las_obras})
def vista_lista_presupuestos(request):
    todos_los_presupuestos = Presupuesto.objects.all().order_by('-id')
    return render(request, 'gestion/lista_presupuestos.html', {'lista_presupuestos': todos_los_presupuestos})
# =========================================================================
# 5. MOTOR CORE ERP: TRANSFORMAR PRESUPUESTO EN OBRA Y DESCONTAR ALMACÉN
# =========================================================================
def procesar_aprobacion_erp(request, presupuesto_id):
    # 1. Buscamos el presupuesto que el cliente acepto
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    
    # Si el presupuesto ya fue procesado antes, evitamos duplicar la operacion
    if presupuesto.estado == 'ACEP':
        return redirect('lista_presupuestos')
        
    # 2. AUTOMATIZACIÓN DE ALMACÉN: Recorremos los materiales y los restamos del stock
    items_presupuesto = presupuesto.items.all() if presupuesto.items.exists() else presupuesto.itempresupuesto_set.all()
    
    for item in items_presupuesto:
        producto_inventario = item.producto
        # Restamos las cantidades físicamente del inventario
        producto_inventario.stock_actual -= int(item.cantidad)
        producto_inventario.save()
        
    # 3. AUTOMATIZACIÓN DE OPERACIONES: Creamos la orden de Trabajo/Obra de forma automática
    nueva_obra = Trabajo.objects.create(
        cliente=presupuesto.cliente,
        titulo=f"OBRA EFECTIVA: Presupuesto #{presupuesto.id}",
        descripcion=f"Materiales cotizados y descontados de almacen:\n" + 
                    "\n".join([f"- {i.cantidad}x {i.producto.nombre}" for i in items_presupuesto]) +
                    f"\n\nNotas adicionales del contrato:\n{presupuesto.notas_adicionales or 'Sin notas.'}",
        monto_cobrado=presupuesto.total_presupuesto, # Inyectamos el cobro real directo al reporte financiero
        estado='PEND' # Queda planificada a la espera de asignarle un tecnico
    )
    
    # 4. Cambiamos el estado del presupuesto a ACEPTADO
    presupuesto.estado = 'ACEP'
    presupuesto.save()
    
    # Redirigimos al usuario directamente a la nueva lista visual de trabajos para que vea su obra creada
    return redirect('lista_trabajos')
from .models import RegistroCompra

def vista_lista_compras(request):
    todas_las_compras = RegistroCompra.objects.all().order_by('-id')
    return render(request, 'gestion/lista_compras.html', {'lista_compras': todas_las_compras})
from django.contrib.auth import authenticate, login

def vista_login_personalizado(request):
    error = False
    if request.method == 'POST':
        usuario_escribio = request.POST.get('username')
        clave_escribio = request.POST.get('password')
        
        # Validamos contra la base de datos de Django
        usuario_valido = authenticate(request, username=usuario_escribio, password=clave_escribio)
        
        if usuario_valido is not None:
            login(request, usuario_valido)
            # Si el inicio es correcto, lo enviamos al Dashboard principal
            return redirect('dashboard')
        else:
            error = True # Activa el recuadro rojo de alerta

    return render(request, 'gestion/login.html', {'error_login': error})
