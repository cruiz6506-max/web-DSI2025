from django.contrib import admin
from .models import (
    Usuario, Mesa, Categoria, Producto,
    Pedido, DetallePedido, Pago
)


# ------------------------------
# ADMIN USUARIO
# ------------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("cedula", "nombre", "apellido", "email", "rol")
    search_fields = ("cedula", "nombre", "apellido", "email")
    list_filter = ("rol",)


# ------------------------------
# ADMIN MESA
# ------------------------------
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ("numero", "capacidad", "estado")
    list_filter = ("estado",)
    search_fields = ("numero",)


# ------------------------------
# ADMIN CATEGORIA
# ------------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


# ------------------------------
# ADMIN PRODUCTO
# ------------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nombre", "categoria__nombre")


# ------------------------------
# ADMIN PEDIDO
# ------------------------------
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "mesa", "tipo_pedido", "estado", "fecha")
    list_filter = ("tipo_pedido", "estado", "fecha")
    search_fields = ("usuario__nombre", "usuario__apellido", "mesa__numero")
    inlines = [DetallePedidoInline]


# ------------------------------
# ADMIN DETALLE PEDIDO
# ------------------------------
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "producto", "cantidad", "subtotal")
    search_fields = ("pedido__id", "producto__nombre")


# ------------------------------
# ADMIN PAGO (Factura)
# ------------------------------
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "pedido", "metodo", "monto", "fecha_pago", "estado")
    list_filter = ("metodo", "estado")
    search_fields = ("pedido__id", "metodo")
