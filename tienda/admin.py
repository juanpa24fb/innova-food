from django.contrib import admin
from .models import Producto, Pedido, DetallePedido, DatosPago


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'precio',
        'cantidad_presentacion',
        'unidad_medida',
        'stock',
        'disponible',
        'creado'
    )
    list_filter = ('disponible', 'unidad_medida', 'creado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'cantidad_presentacion', 'unidad_medida', 'stock', 'disponible')
    readonly_fields = ('creado',)


@admin.register(DatosPago)
class DatosPagoAdmin(admin.ModelAdmin):
    list_display = ('banco', 'tipo_cuenta', 'numero_cuenta', 'titular', 'whatsapp', 'actualizado')
    readonly_fields = ('actualizado',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'nombre_cliente',
        'telefono',
        'tipo_compra',
        'pago_credito',
        'subtotal_sin_interes',
        'interes',
        'total',
        'estado',
        'fecha'
    )
    list_filter = ('estado', 'tipo_compra', 'pago_credito', 'fecha')
    search_fields = ('usuario__username', 'nombre_cliente', 'telefono', 'direccion')
    list_editable = ('estado',)
    readonly_fields = (
        'usuario',
        'nombre_cliente',
        'telefono',
        'direccion',
        'tipo_compra',
        'pago_credito',
        'subtotal_sin_interes',
        'interes',
        'total',
        'comprobante',
        'fecha'
    )
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('producto__nombre', 'pedido__usuario__username')
