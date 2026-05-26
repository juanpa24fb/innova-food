from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    UNIDADES_MEDIDA = [
        ('unidad', 'Unidad'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    cantidad_presentacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad de presentación"
    )
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='unidad',
        verbose_name="Unidad de medida"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Unidades disponibles")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del producto")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado']

    def __str__(self):
        return self.nombre

    @property
    def presentacion(self):
        cantidad = self.cantidad_presentacion

        if cantidad == int(cantidad):
            cantidad = int(cantidad)

        if self.unidad_medida == 'unidad':
            if cantidad == 1:
                return "1 unidad"
            return f"{cantidad} unidades"

        return f"{cantidad} {self.unidad_medida}"


class DatosPago(models.Model):
    banco = models.CharField(max_length=100, verbose_name="Banco")
    tipo_cuenta = models.CharField(max_length=50, verbose_name="Tipo de cuenta")
    numero_cuenta = models.CharField(max_length=50, verbose_name="Número de cuenta")
    titular = models.CharField(max_length=120, verbose_name="Titular de la cuenta")
    identificacion = models.CharField(max_length=20, blank=True, verbose_name="Cédula o RUC")
    correo = models.EmailField(blank=True, verbose_name="Correo del titular")
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="Número de WhatsApp")
    mensaje_whatsapp = models.TextField(
        blank=True,
        default="Hola, deseo realizar una consulta sobre Innova Food.",
        verbose_name="Mensaje inicial de WhatsApp"
    )
    nota = models.TextField(blank=True, verbose_name="Nota adicional")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Dato de pago"
        verbose_name_plural = "Datos de pago"

    def __str__(self):
        return f"{self.banco} - {self.numero_cuenta}"

    def whatsapp_link(self):
        if not self.whatsapp:
            return ""
        numero = self.whatsapp.replace("+", "").replace(" ", "").replace("-", "")
        mensaje = self.mensaje_whatsapp.replace(" ", "%20")
        return f"https://wa.me/{numero}?text={mensaje}"


class Pedido(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Comprobante enviado', 'Comprobante enviado'),
        ('Pagado', 'Pagado'),
        ('Rechazado', 'Rechazado'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
    ]

    TIPOS_COMPRA = [
        ('menor', 'Compra al por menor'),
        ('mayor', 'Compra al por mayor'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Comprador")
    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre del cliente")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.TextField(verbose_name="Dirección de entrega")

    tipo_compra = models.CharField(
        max_length=20,
        choices=TIPOS_COMPRA,
        default='menor',
        verbose_name="Tipo de compra"
    )
    pago_credito = models.BooleanField(default=False, verbose_name="Pago a crédito")
    subtotal_sin_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal")
    interes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Interés aplicado")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    estado = models.CharField(max_length=30, choices=ESTADOS, default='Pendiente', verbose_name="Estado del pedido")
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True, verbose_name="Comprobante de pago")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del pedido")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles', verbose_name="Pedido")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Detalle del pedido"
        verbose_name_plural = "Detalles del pedido"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
