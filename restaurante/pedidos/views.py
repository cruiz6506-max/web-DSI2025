from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal

from django.views.decorators.http import require_http_methods

from .models import Usuario, Producto, Categoria, Mesa, Pedido, DetallePedido, Pago
import json

def inicio(request):
    return render(request, 'index.html')


# ===========================
# MÓDULO USUARIO
# ===========================

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        contraseña = request.POST.get("contraseña")

        try:
            usuario = Usuario.objects.get(email=email)

            if usuario.checkpassword(contraseña):
                request.session['usuario_id'] = usuario.id
                request.session['rol'] = usuario.rol

                rol = usuario.rol.strip().lower()

                if rol == "administrador":
                    return redirect('admin_dashboard')
                elif rol == "cliente":
                    return redirect('home_cliente')
                elif rol == "cajero":
                    return redirect('admin_dashboard')
                elif rol == "mesero":
                    return redirect('admin_dashboard')
                elif rol == "repartidor":
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Rol de usuario no reconocido.")
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "El correo no está registrado.")

    return render(request, 'C1_Usuario/login.html')


def registro_view(request):
    if request.method == 'POST':
        usuario = Usuario(
            cedula=request.POST.get('cedula'),
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            email=request.POST.get('email'),
            contraseña=make_password(request.POST.get('password')),
            rol=request.POST.get('rol'),
            pregunta_clave=request.POST.get('pregunta_clave'),
            respuesta_clave=request.POST.get('respuesta_clave')
        )

        usuario.save()
        request.session['usuario_id'] = usuario.id
        messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'C1_Usuario/registro.html')


def clave_olvidada(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        respuesta = request.POST.get('respuesta')

        try:
            usuario = Usuario.objects.get(email=email)
            request.session['email_recuperacion'] = email
        except Usuario.DoesNotExist:
            messages.error(request, 'No se encuentra un usuario con ese correo electrónico.')
            return render(request, 'C1_Usuario/clave_olvidada.html')

        if respuesta:
            if usuario.respuesta_clave.strip().lower() == respuesta.strip().lower():
                return redirect('clave_cambiada')
            else:
                messages.error(request, 'La respuesta a la pregunta de seguridad es incorrecta.')
                return render(request, 'C1_Usuario/clave_olvidada.html', {
                    'email': email,
                    'pregunta_clave': usuario.pregunta_clave,
                })
        else:
            return render(request, 'C1_Usuario/clave_olvidada.html', {
                'email': email,
                'pregunta_clave': usuario.pregunta_clave,
            })

    return render(request, 'C1_Usuario/clave_olvidada.html')


def clave_cambiada(request):
    if request.method == 'POST':
        nueva_clave = request.POST.get('new-password')
        repetir_clave = request.POST.get('password-repeat')
        email = request.session.get('email_recuperacion')

        if not email:
            messages.error(request, "No se encontró el correo del usuario.")
            return redirect('Clave_Olvidada')

        if not nueva_clave or not repetir_clave:
            messages.error(request, "Completa todos los campos.")
            return redirect('clave_cambiada')

        if nueva_clave != repetir_clave:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('clave_cambiada')

        try:
            usuario = Usuario.objects.get(email=email)
            usuario.contraseña = make_password(nueva_clave)
            usuario.save()

            del request.session['email_recuperacion']
            messages.success(request, "Tu contraseña se cambió correctamente.")
            return redirect('login')

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('clave_olvidada')

    return render(request, 'C1_Usuario/clave_cambiada.html')


# ===========================
# MÓDULO CLIENTE
# ===========================

def home_cliente(request):
    productos = Producto.objects.all()
    categoria_seleccionada = request.GET.get('categoria', 'Todos')
    productos = Producto.objects.all()

    if categoria_seleccionada != 'Todos':
        productos = productos.filter(categoria__nombre=categoria_seleccionada)

    return render(request, 'Vistas/Vista_cliente/homeCliente.html', {
        'productos': productos,
        'categoria_seleccionada': categoria_seleccionada,
        'usuario': request.user,
    })


# ===========================
# MÓDULO ADMINISTRADOR
# ===========================

def admin_dashboard(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    return render(request, 'Vistas/Vista_Admin/base_admin.html', {
        'usuario': usuario,
        'total_usuarios': Usuario.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_mesas': Mesa.objects.count(),
        'total_pedidos': Pedido.objects.count(),
    })


def usuarios_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    buscar = request.GET.get('buscar', '')
    usuarios = Usuario.objects.all().order_by('-id')

    if buscar:
        usuarios = usuarios.filter(
            Q(nombre__icontains=buscar) |
            Q(apellido__icontains=buscar) |
            Q(email__icontains=buscar) |
            Q(cedula__icontains=buscar)
        )

    return render(request, 'Vistas/Vista_Admin/usuarios_list.html', {
        'usuarios': usuarios,
        'usuario': usuario,
        'buscar': buscar
    })


def usuarios_create(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    if request.method == 'POST':
        if Usuario.objects.filter(email=request.POST.get('email')).exists():
            messages.error(request, 'Ya existe un usuario con ese email')
            return render(request, 'Vistas/Vista_Admin/usuarios_form.html', {'usuario': usuario})

        if Usuario.objects.filter(cedula=request.POST.get('cedula')).exists():
            messages.error(request, 'Ya existe un usuario con esa cédula')
            return render(request, 'Vistas/Vista_Admin/usuarios_form.html', {'usuario': usuario})

        Usuario.objects.create(
            cedula=request.POST.get('cedula'),
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            email=request.POST.get('email'),
            contraseña=make_password(request.POST.get('contraseña')),
            rol=request.POST.get('rol'),
            pregunta_clave=request.POST.get('pregunta_clave'),
            respuesta_clave=request.POST.get('respuesta_clave')
        )

        messages.success(request, 'Usuario creado exitosamente')
        return redirect('usuarios_list')

    return render(request, 'Vistas/Vista_Admin/usuarios_form.html', {'usuario': usuario})


def usuarios_edit(request, id):
    usuario_logueado = Usuario.objects.get(id=request.session.get('usuario_id'))
    usuario_editar = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        usuario_editar.cedula = request.POST.get('cedula')
        usuario_editar.nombre = request.POST.get('nombre')
        usuario_editar.apellido = request.POST.get('apellido')
        usuario_editar.email = request.POST.get('email')
        usuario_editar.rol = request.POST.get('rol')
        usuario_editar.pregunta_clave = request.POST.get('pregunta_clave')
        usuario_editar.respuesta_clave = request.POST.get('respuesta_clave')

        if request.POST.get('contraseña'):
            usuario_editar.contraseña = make_password(request.POST.get('contraseña'))

        usuario_editar.save()
        messages.success(request, 'Usuario actualizado exitosamente')
        return redirect('usuarios_list')

    return render(request, 'Vistas/Vista_Admin/usuarios_form.html', {
        'usuario': usuario_logueado,
        'usuario_editar': usuario_editar
    })


def usuarios_delete(request, id):
    usuario = Usuario.objects.get(id=request.session.get('usuario_id'))
    usuario_eliminar = get_object_or_404(Usuario, id=id)

    if usuario.id == usuario_eliminar.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta')
        return redirect('usuarios_list')

    usuario_eliminar.delete()
    messages.success(request, 'Usuario eliminado exitosamente')
    return redirect('usuarios_list')


# ===========================
# MÓDULO PRODUCTOS
# ===========================

def productos_list(request):
    return render(request, 'Vistas/Vista_Admin/productos_list.html', {
        'productos': Producto.objects.all()
    })


def productos_nuevo(request):
    if request.method == 'POST':
        producto = Producto(
            nombre=request.POST.get('nombre'),
            categoria=Categoria.objects.get(nombre=request.POST.get('categoria')),
            precio=request.POST.get('precio'),
            imagen=request.FILES.get('imagen')
        )
        producto.save()
        messages.success(request, 'Producto creado correctamente')
        return redirect('productos_list')

    return render(request, 'Vistas/Vista_Admin/productos_form.html', {'producto': None})


def productos_editar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.categoria = Categoria.objects.get(nombre=request.POST.get('categoria'))

        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')

        producto.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('productos_list')

    return render(request, 'Vistas/Vista_Admin/productos_form.html', {'producto': producto})


def productos_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente')
    return redirect('productos_list')


# ===========================
# MÓDULO MESAS
# ===========================

def mesas_list(request):
    return render(request, 'Vistas/Vista_Admin/mesas_list.html', {
        'mesas': Mesa.objects.all().order_by('numero')
    })


def mesas_nuevo(request):
    if request.method == 'POST':
        Mesa.objects.create(
            numero=request.POST.get('numero'),
            capacidad=request.POST.get('capacidad'),
            estado=request.POST.get('estado')
        )
        messages.success(request, 'Mesa creada correctamente')
        return redirect('mesas_list')

    return render(request, 'Vistas/Vista_Admin/mesas_form.html', {'mesa': None})


def mesas_editar(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    if request.method == 'POST':
        mesa.numero = request.POST.get('numero')
        mesa.capacidad = request.POST.get('capacidad')
        mesa.estado = request.POST.get('estado')
        mesa.save()
        messages.success(request, 'Mesa actualizada')
        return redirect('mesas_list')

    return render(request, 'Vistas/Vista_Admin/mesas_form.html', {'mesa': mesa})


def mesas_eliminar(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.delete()
    messages.success(request, 'Mesa eliminada')
    return redirect('mesas_list')
# ===========================
# MÓDULO PEDIDOS
# ===========================
def pedidos_list(request):
    # Verificar sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    # Filtros
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')
    buscar = request.GET.get('buscar', '')

    pedidos = Pedido.objects.select_related('usuario', 'mesa').prefetch_related('detalles__producto').order_by('-fecha')

    if estado_filtro:
        pedidos = pedidos.filter(estado=estado_filtro)

    if tipo_filtro:
        pedidos = pedidos.filter(tipo_pedido=tipo_filtro)

    if buscar:
        pedidos = pedidos.filter(
            Q(usuario__nombre__icontains=buscar) |
            Q(usuario__apellido__icontains=buscar) |
            Q(id__icontains=buscar)
        )

    # Calcular total de cada pedido
    pedidos_con_total = []
    for pedido in pedidos:
        total = sum(detalle.subtotal for detalle in pedido.detalles.all())
        pedidos_con_total.append({
            'pedido': pedido,
            'total': total
        })

    return render(request, 'Vistas/Vista_Admin/pedidos_list.html', {
        'pedidos_con_total': pedidos_con_total,
        'usuario': usuario,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'buscar': buscar
    })


def pedidos_create(request):
    """Crear nuevo pedido"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    if request.method == 'POST':
        try:
            # Datos del pedido
            cliente_id = request.POST.get('cliente_id')
            tipo_pedido = request.POST.get('tipo_pedido')
            mesa_id = request.POST.get('mesa_id')
            estado = request.POST.get('estado', 'pendiente')

            # Validar cliente
            if not Usuario.objects.filter(id=cliente_id).exists():
                messages.error(request, 'Cliente no encontrado')
                return redirect('pedidos_create')

            # Crear pedido
            pedido = Pedido(
                usuario_id=cliente_id,
                tipo_pedido=tipo_pedido,
                estado=estado
            )

            # Asignar mesa si es tipo local
            if tipo_pedido == 'local' and mesa_id:
                pedido.mesa_id = mesa_id
                # Cambiar estado de la mesa a ocupada
                mesa = Mesa.objects.get(id=mesa_id)
                mesa.estado = 'ocupada'
                mesa.save()

            pedido.save()

            # Agregar productos (detalles del pedido)
            productos_ids = request.POST.getlist('producto_id[]')
            cantidades = request.POST.getlist('cantidad[]')

            if not productos_ids:
                messages.error(request, 'Debe agregar al menos un producto al pedido')
                pedido.delete()
                return redirect('pedidos_create')

            for producto_id, cantidad in zip(productos_ids, cantidades):
                if producto_id and cantidad:
                    producto = Producto.objects.get(id=producto_id)
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=int(cantidad),
                        subtotal=producto.precio * int(cantidad)
                    )

            messages.success(request, f'Pedido #{pedido.id} creado exitosamente')
            return redirect('pedidos_detail', id=pedido.id)

        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')

    # Obtener datos para el formulario
    clientes = Usuario.objects.all()
    productos = Producto.objects.all()
    mesas_disponibles = Mesa.objects.filter(estado='disponible')

    return render(request, 'Vistas/Vista_Admin/pedidos_form.html', {
        'usuario': usuario,
        'clientes': clientes,
        'productos': productos,
        'mesas_disponibles': mesas_disponibles
    })


def pedidos_detail(request, id):
    """Ver detalle completo de un pedido"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    pedido = get_object_or_404(Pedido.objects.select_related('usuario', 'mesa'), id=id)
    detalles = pedido.detalles.select_related('producto').all()

    # Calcular total
    total = sum(detalle.subtotal for detalle in detalles)

    # Verificar si tiene pago
    try:
        pago = Pago.objects.get(pedido=pedido)
    except Pago.DoesNotExist:
        pago = None

    return render(request, 'Vistas/Vista_Admin/pedidos_detail.html', {
        'usuario': usuario,
        'pedido': pedido,
        'detalles': detalles,
        'total': total,
        'pago': pago
    })


def pedidos_edit(request, id):
    """Editar pedido existente"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    pedido = get_object_or_404(Pedido, id=id)
    detalles_actuales = pedido.detalles.all()

    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            tipo_pedido = request.POST.get('tipo_pedido')
            mesa_id = request.POST.get('mesa_id')
            estado = request.POST.get('estado')

            # Liberar mesa anterior si existía
            if pedido.mesa:
                mesa_anterior = pedido.mesa
                mesa_anterior.estado = 'disponible'
                mesa_anterior.save()

            pedido.tipo_pedido = tipo_pedido
            pedido.estado = estado

            # Asignar nueva mesa si es necesario
            if tipo_pedido == 'local' and mesa_id:
                pedido.mesa_id = mesa_id
                mesa = Mesa.objects.get(id=mesa_id)
                mesa.estado = 'ocupada'
                mesa.save()
            else:
                pedido.mesa = None

            pedido.save()

            # Eliminar detalles antiguos
            pedido.detalles.all().delete()

            # Agregar nuevos productos
            productos_ids = request.POST.getlist('producto_id[]')
            cantidades = request.POST.getlist('cantidad[]')

            for producto_id, cantidad in zip(productos_ids, cantidades):
                if producto_id and cantidad:
                    producto = Producto.objects.get(id=producto_id)
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=int(cantidad),
                        subtotal=producto.precio * int(cantidad)
                    )

            messages.success(request, f'Pedido #{pedido.id} actualizado exitosamente')
            return redirect('pedidos_detail', id=pedido.id)

        except Exception as e:
            messages.error(request, f'Error al actualizar pedido: {str(e)}')

    clientes = Usuario.objects.all()
    productos = Producto.objects.all()
    mesas_disponibles = Mesa.objects.filter(estado='disponible')

    return render(request, 'Vistas/Vista_Admin/pedidos_form.html', {
        'usuario': usuario,
        'pedido': pedido,
        'detalles_actuales': detalles_actuales,
        'clientes': clientes,
        'productos': productos,
        'mesas_disponibles': mesas_disponibles
    })


def pedidos_delete(request, id):
    """Eliminar pedido"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol.strip().lower() != 'administrador':
        return redirect('login')

    if request.method == 'POST':
        try:
            pedido = get_object_or_404(Pedido, id=id)

            # Liberar mesa si está ocupada
            if pedido.mesa:
                mesa = pedido.mesa
                mesa.estado = 'disponible'
                mesa.save()

            pedido_id = pedido.id
            pedido.delete()
            messages.success(request, f'Pedido #{pedido_id} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar pedido: {str(e)}')

    return redirect('pedidos_list')


def pedidos_cambiar_estado(request, id):
    """Cambiar estado del pedido (AJAX)"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        try:
            pedido = get_object_or_404(Pedido, id=id)
            nuevo_estado = request.POST.get('estado')

            pedido.estado = nuevo_estado
            pedido.save()

            # Si el estado es "entregado" y la mesa está ocupada, liberarla
            if nuevo_estado == 'entregado' and pedido.mesa:
                mesa = pedido.mesa
                mesa.estado = 'disponible'
                mesa.save()

            messages.success(request, f'Estado del pedido #{pedido.id} cambiado a "{nuevo_estado}"')
        except Exception as e:
            messages.error(request, f'Error al cambiar estado: {str(e)}')

    return redirect('pedidos_detail', id=id)
# ===============================
# MODULO DE PAGOS
# ===============================
def pagos_list(request):
    pagos = Pago.objects.select_related('pedido', 'pedido__usuario').order_by('-fecha_pago')
    return render(request, 'Vistas/Vista_Admin/pagos_list.html', {
        'pagos': pagos
    })

def registrar_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if hasattr(pedido, 'pago'):
        messages.warning(request, 'Este pedido ya tiene un pago registrado.')
        return redirect('pagos_list')

    total = sum(d.subtotal for d in pedido.detalles.all())

    if request.method == 'POST':
        Pago.objects.create(
            pedido=pedido,
            metodo=request.POST['metodo'],
            monto=Decimal(total),
            direccion_entrega=request.POST.get('direccion_entrega'),
            telefono_contacto=request.POST.get('telefono_contacto')
        )

        pedido.estado = 'pagado'
        pedido.save()

        messages.success(request, 'Pago registrado correctamente.')
        return redirect('pagos_list')

    return render(request, 'Vistas/Vista_Admin/pago_form.html', {
        'pedido': pedido,
        'total': total
    })


def editar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pedido = pago.pedido

    if request.method == 'POST':
        pago.metodo = request.POST['metodo']
        pago.direccion_entrega = request.POST.get('direccion_entrega')
        pago.telefono_contacto = request.POST.get('telefono_contacto')
        pago.save()

        messages.success(request, 'Pago actualizado correctamente.')
        return redirect('pagos_list')

    return render(request, 'Vistas/Vista_Admin/pago_edit.html', {
        'pago': pago,
        'pedido': pedido
    })


def eliminar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pedido = pago.pedido

    if request.method == 'POST':
        pago.delete()
        pedido.estado = 'pendiente'
        pedido.save()

        messages.success(request, 'Pago eliminado correctamente.')
        return redirect('pagos_list')

    return render(request, 'Vistas/Vista_Admin/pago_delete.html', {
        'pago': pago
    })


# ---------------------------
# CLIENTE - Procesar Pedido
# ---------------------------

@require_http_methods(["POST"])
def procesar_pedido_cliente(request):
    """Procesa el carrito y crea un pedido"""
    try:
        # Verificar sesión del cliente
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({
                'success': False,
                'message': 'Debe iniciar sesión'
            })

        usuario = Usuario.objects.get(id=usuario_id)

        # Obtener datos del carrito
        data = json.loads(request.body)
        carrito = data.get('carrito', [])

        if not carrito:
            return JsonResponse({
                'success': False,
                'message': 'El carrito está vacío'
            })

        # Crear el pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            tipo_pedido='para_llevar',  # Por defecto para llevar desde web
            estado='pendiente'
        )

        # Crear los detalles del pedido
        total = 0
        for item in carrito:
            producto = Producto.objects.get(id=item['id'])
            cantidad = int(item['cantidad'])
            subtotal = producto.precio * cantidad

            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                subtotal=subtotal
            )

            total += subtotal

        # Guardar el pedido_id y total en la sesión para la pasarela de pago
        request.session['pedido_pendiente_id'] = pedido.id
        request.session['pedido_total'] = float(total)

        return JsonResponse({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'pedido_id': pedido.id,
            'total': float(total)
        })

    except Usuario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no encontrado'
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar el pedido: {str(e)}'
        })


# ---------------------------
# CLIENTE - Pasarela de Pago
# ---------------------------

def pasarela_pago(request):
    """Vista de la pasarela de pago"""
    # Verificar sesión del cliente
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Debe iniciar sesión')
        return redirect('login')

    # Obtener el pedido pendiente de la sesión
    pedido_id = request.session.get('pedido_pendiente_id')
    if not pedido_id:
        messages.error(request, 'No hay pedido pendiente')
        return redirect('home_cliente')

    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario_id=usuario_id)
        detalles = pedido.detalles.all()

        # Calcular total
        total = sum(detalle.subtotal for detalle in detalles)

        context = {
            'pedido': pedido,
            'detalles': detalles,
            'total': total
        }

        return render(request, 'Vistas/Vista_cliente/pasarela_pago.html', context)

    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido no encontrado')
        return redirect('home_cliente')


def confirmar_pago(request):
    """Procesar la confirmación del pago"""
    if request.method == 'POST':
        try:
            # Verificar sesión
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.error(request, 'Debe iniciar sesión')
                return redirect('login')

            # Obtener datos del formulario
            pedido_id = request.POST.get('pedido_id')
            metodo = request.POST.get('metodo')
            tipo_pedido = request.POST.get('tipo_pedido')
            direccion = request.POST.get('direccion', '')
            telefono = request.POST.get('telefono')
            notas = request.POST.get('notas', '')

            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id, usuario_id=usuario_id)

            # Actualizar tipo de pedido
            pedido.tipo_pedido = tipo_pedido
            pedido.estado = 'en preparación'  # Cambiar estado a en preparación
            pedido.save()

            # Calcular total
            total = sum(detalle.subtotal for detalle in pedido.detalles.all())

            # Crear el pago
            pago = Pago.objects.create(
                pedido=pedido,
                metodo=metodo,
                monto=total,
                direccion_entrega=direccion if tipo_pedido == 'domicilio' else '',
                telefono_contacto=telefono,
                estado='completado'
            )

            # Limpiar sesión
            if 'pedido_pendiente_id' in request.session:
                del request.session['pedido_pendiente_id']
            if 'pedido_total' in request.session:
                del request.session['pedido_total']

            # Redirigir a confirmación
            request.session['pago_exitoso'] = True
            request.session['pedido_confirmado_id'] = pedido.id

            return redirect('confirmacion_pedido')

        except Pedido.DoesNotExist:
            messages.error(request, 'Pedido no encontrado')
            return redirect('home_cliente')
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return redirect('pasarela_pago')

    return redirect('home_cliente')


def confirmacion_pedido(request):
    """Página de confirmación de pedido exitoso"""
    # Verificar que haya un pago exitoso en la sesión
    if not request.session.get('pago_exitoso'):
        return redirect('home_cliente')

    pedido_id = request.session.get('pedido_confirmado_id')

    try:
        pedido = Pedido.objects.get(id=pedido_id)
        pago = Pago.objects.get(pedido=pedido)
        detalles = pedido.detalles.all()
        total = sum(detalle.subtotal for detalle in detalles)

        # Limpiar flags de sesión
        del request.session['pago_exitoso']
        del request.session['pedido_confirmado_id']

        context = {
            'pedido': pedido,
            'pago': pago,
            'detalles': detalles,
            'total': total
        }

        return render(request, 'Vistas/Vista_cliente/confirmacion_pedido.html', context)

    except (Pedido.DoesNotExist, Pago.DoesNotExist):
        messages.error(request, 'Error al cargar la confirmación')
        return redirect('home_cliente')