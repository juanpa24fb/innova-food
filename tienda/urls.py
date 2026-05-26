from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('categorias/', views.categorias, name='categorias'),
    path('beneficios/', views.beneficios, name='beneficios'),
    path('contacto/', views.contacto, name='contacto'),

    path('productos/', views.productos, name='productos'),

    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    path('carrito/', views.ver_carrito, name='carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('quitar-carrito/<int:producto_id>/', views.quitar_carrito, name='quitar_carrito'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),

    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('subir-comprobante/<int:pedido_id>/', views.subir_comprobante, name='subir_comprobante'),

    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('datos-pago/', views.administrar_datos_pago, name='datos_pago'),

    path('admin-productos/', views.admin_productos, name='admin_productos'),
    path('admin-productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('admin-productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin-productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    path('admin-pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin-pedidos/estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('admin-pedidos/factura/<int:pedido_id>/', views.descargar_factura, name='descargar_factura'),
]
