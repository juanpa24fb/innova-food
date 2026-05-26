from django.contrib import admin
from .models import Producto, Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'disponible', 'creado')
    list_filter = ('disponible', 'creado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'disponible')
    readonly_fields = ('creado',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombre_cliente', 'telefono', 'total', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username', 'nombre_cliente', 'telefono', 'direccion')
    list_editable = ('estado',)
    readonly_fields = ('usuario', 'nombre_cliente', 'telefono', 'direccion', 'total', 'comprobante', 'fecha')
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('producto__nombre', 'pedido__usuario__username')