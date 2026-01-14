from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('clave_olvidada/', views.clave_olvidada, name='Clave_Olvidada'),
    path('clave_cambiada/', views.clave_cambiada, name='clave_cambiada'),
    path('home-Vista_cliente/', views.home_cliente, name='home_cliente'),
    # Dashboard Admin
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Módulo Usuarios
    path('panel/usuarios/', views.usuarios_list, name='usuarios_list'),
    path('panel/usuarios/nuevo/', views.usuarios_create, name='usuarios_create'),
    path('panel/usuarios/editar/<int:id>/', views.usuarios_edit, name='usuarios_edit'),
    path('panel/usuarios/eliminar/<int:id>/', views.usuarios_delete, name='usuarios_delete'),
    # Módulo Productos
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/nuevo/', views.productos_nuevo, name='productos_nuevo'),
    path('productos/editar/<int:producto_id>/', views.productos_editar, name='productos_editar'),
    path('productos/eliminar/<int:producto_id>/', views.productos_eliminar, name='productos_eliminar'),
    # Módulo mesas
    path('mesas/', views.mesas_list, name='mesas_list'),
    path('mesas/nuevo/', views.mesas_nuevo, name='mesas_nuevo'),
    path('mesas/editar/<int:mesa_id>/', views.mesas_editar, name='mesas_editar'),
    path('mesas/eliminar/<int:mesa_id>/', views.mesas_eliminar, name='mesas_eliminar'),
    # Módulo pedidos
    path('panel/pedidos/', views.pedidos_list, name='pedidos_list'),
    path('panel/pedidos/nuevo/', views.pedidos_create, name='pedidos_create'),
    path('panel/pedidos/ver/<int:id>/', views.pedidos_detail, name='pedidos_detail'),
    path('panel/pedidos/editar/<int:id>/', views.pedidos_edit, name='pedidos_edit'),
    path('panel/pedidos/eliminar/<int:id>/', views.pedidos_delete, name='pedidos_delete'),
    path('panel/pedidos/cambiar-estado/<int:id>/', views.pedidos_cambiar_estado, name='pedidos_cambiar_estado'),
    # Módulo pagos
    path('pagos/', views.pagos_list, name='pagos_list'),
    path('pedidos/<int:pedido_id>/pagar/',  views.registrar_pago, name='registrar_pago'),
    path('pagos/<int:pago_id>/editar/',  views.editar_pago, name='editar_pago'),
    path('pagos/<int:pago_id>/eliminar/',  views.eliminar_pago, name='eliminar_pago'),

    # Cliente
    path('home-Vista_cliente/', views.home_cliente, name='home_cliente'),
    path('procesar-pedido/', views.procesar_pedido_cliente, name='procesar_pedido_cliente'),
    path('pasarela-pago/', views.pasarela_pago, name='pasarela_pago'),
    path('confirmar-pago/', views.confirmar_pago, name='confirmar_pago'),
    path('confirmacion-pedido/', views.confirmacion_pedido, name='confirmacion_pedido'),

]

