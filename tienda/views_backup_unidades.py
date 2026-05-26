from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

from .models import Producto, Pedido, DetallePedido, DatosPago
from .forms import RegistroForm, ProductoForm, PedidoForm, ComprobanteForm, DatosPagoForm


def es_admin(user):
    return user.is_staff or user.is_superuser


def inicio(request):
    productos = Producto.objects.filter(disponible=True, stock__gt=0).order_by("-creado")[:6]
    return render(request, "tienda/inicio.html", {"productos": productos})


def categorias(request):
    return render(request, "tienda/categorias.html")


def beneficios(request):
    return render(request, "tienda/beneficios.html")


def contacto(request):
    datos_pago = DatosPago.objects.first()
    return render(request, "tienda/contacto.html", {"datos_pago": datos_pago})


def productos(request):
    productos = Producto.objects.all().order_by("-creado")
    return render(request, "tienda/productos.html", {"productos": productos})


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )
            login(request, usuario)
            messages.success(request, "Registro exitoso. Bienvenido a Innova Food.")
            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(request, "tienda/registro.html", {"form": form})


def iniciar_sesion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            if usuario.is_staff or usuario.is_superuser:
                return redirect("panel_admin")
            return redirect("inicio")

        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "tienda/login.html")


def cerrar_sesion(request):
    logout(request)
    return redirect("inicio")


def obtener_carrito(request):
    return request.session.get("carrito", {})


def guardar_carrito(request, carrito):
    request.session["carrito"] = carrito
    request.session.modified = True


@login_required
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if not producto.disponible or producto.stock <= 0:
        messages.error(request, "Este producto no está disponible.")
        return redirect("productos")

    carrito = obtener_carrito(request)
    producto_id_str = str(producto_id)
    cantidad_actual = carrito.get(producto_id_str, 0)

    if cantidad_actual >= producto.stock:
        messages.warning(request, "No hay más stock disponible para este producto.")
    else:
        carrito[producto_id_str] = cantidad_actual + 1
        guardar_carrito(request, carrito)
        messages.success(request, "Producto agregado al carrito.")

    return redirect("productos")


@login_required
def quitar_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto_id_str = str(producto_id)

    if producto_id_str in carrito:
        carrito[producto_id_str] -= 1

        if carrito[producto_id_str] <= 0:
            del carrito[producto_id_str]

        guardar_carrito(request, carrito)

    return redirect("carrito")


@login_required
def ver_carrito(request):
    carrito = obtener_carrito(request)
    items = []
    total = Decimal("0.00")

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal

        items.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal,
        })

    return render(request, "tienda/carrito.html", {"items": items, "total": total})


@login_required
def finalizar_compra(request):
    carrito = obtener_carrito(request)

    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("productos")

    items = []
    subtotal_general = Decimal("0.00")
    aplica_mayorista = False

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        subtotal = producto.precio * cantidad
        subtotal_general += subtotal

        if cantidad >= 12:
            aplica_mayorista = True

        items.append((producto, cantidad, subtotal))

    interes = Decimal("0.00")
    total = subtotal_general

    if request.method == "POST":
        form = PedidoForm(request.POST)

        if form.is_valid():
            tipo_compra = form.cleaned_data["tipo_compra"]
            pago_credito = form.cleaned_data["pago_credito"]

            if tipo_compra == "mayor" and pago_credito and aplica_mayorista:
                interes = (subtotal_general * Decimal("0.08")).quantize(Decimal("0.01"))
                total = subtotal_general + interes
            else:
                pago_credito = False
                interes = Decimal("0.00")
                total = subtotal_general

            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.tipo_compra = tipo_compra
            pedido.pago_credito = pago_credito
            pedido.subtotal_sin_interes = subtotal_general
            pedido.interes = interes
            pedido.total = total
            pedido.estado = "Pendiente"
            pedido.save()

            for producto, cantidad, subtotal in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal
                )

                producto.stock -= cantidad

                if producto.stock <= 0:
                    producto.stock = 0
                    producto.disponible = False

                producto.save()

            guardar_carrito(request, {})
            messages.success(request, "Pedido creado. Ahora sube tu comprobante de pago.")
            return redirect("subir_comprobante", pedido_id=pedido.id)
    else:
        form = PedidoForm()

    return render(request, "tienda/finalizar_compra.html", {
        "form": form,
        "items": items,
        "subtotal_general": subtotal_general,
        "total": total,
        "aplica_mayorista": aplica_mayorista,
    })


@login_required
def subir_comprobante(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    datos_pago = DatosPago.objects.first()

    if request.method == "POST":
        form = ComprobanteForm(request.POST, request.FILES, instance=pedido)

        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.estado = "Comprobante enviado"
            pedido.save()
            messages.success(request, "Comprobante enviado correctamente. El administrador revisará tu pago.")
            return redirect("mis_pedidos")
    else:
        form = ComprobanteForm(instance=pedido)

    return render(request, "tienda/subir_comprobante.html", {
        "form": form,
        "pedido": pedido,
        "datos_pago": datos_pago,
    })


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-fecha")
    return render(request, "tienda/mis_pedidos.html", {"pedidos": pedidos})


@login_required
@user_passes_test(es_admin)
def panel_admin(request):
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado="Comprobante enviado").count()
    total_usuarios = User.objects.filter(is_staff=False).count()
    datos_pago = DatosPago.objects.first()

    return render(request, "tienda/panel_admin.html", {
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "pedidos_pendientes": pedidos_pendientes,
        "total_usuarios": total_usuarios,
        "datos_pago": datos_pago,
    })


@login_required
@user_passes_test(es_admin)
def administrar_datos_pago(request):
    datos_pago = DatosPago.objects.first()

    if request.method == "POST":
        form = DatosPagoForm(request.POST, instance=datos_pago)

        if form.is_valid():
            form.save()
            messages.success(request, "Datos de pago y WhatsApp guardados correctamente.")
            return redirect("panel_admin")
    else:
        form = DatosPagoForm(instance=datos_pago)

    return render(request, "tienda/datos_pago.html", {
        "form": form,
        "datos_pago": datos_pago,
    })


@login_required
@user_passes_test(es_admin)
def admin_productos(request):
    productos = Producto.objects.all().order_by("-creado")
    return render(request, "tienda/admin_productos.html", {"productos": productos})


@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("admin_productos")
    else:
        form = ProductoForm()

    return render(request, "tienda/producto_form.html", {
        "form": form,
        "titulo": "Nuevo producto",
    })


@login_required
@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("admin_productos")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "tienda/producto_form.html", {
        "form": form,
        "titulo": "Editar producto",
    })


@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect("admin_productos")


@login_required
@user_passes_test(es_admin)
def admin_pedidos(request):
    pedidos = Pedido.objects.all().order_by("-fecha")
    return render(request, "tienda/admin_pedidos.html", {"pedidos": pedidos})


@login_required
@user_passes_test(es_admin)
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, "Estado del pedido actualizado.")

    return redirect("admin_pedidos")


@login_required
@user_passes_test(es_admin)
def descargar_factura(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()
    fecha_descarga = timezone.now().strftime("%d/%m/%Y %H:%M")

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Factura Pedido #{pedido.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; color: #111; padding: 30px; }}
            .header {{ border-bottom: 3px solid #1faa59; padding-bottom: 15px; margin-bottom: 25px; }}
            h1 {{ color: #1faa59; margin: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #1faa59; color: white; }}
            .totales {{ margin-top: 25px; text-align: right; }}
            .nota {{ margin-top: 30px; font-size: 13px; color: #555; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>INNOVA FOOD</h1>
            <p><strong>Factura / Comprobante de pedido</strong></p>
            <p>Fecha de descarga: {fecha_descarga}</p>
        </div>

        <h2>Pedido #{pedido.id}</h2>
        <p><strong>Cliente:</strong> {pedido.nombre_cliente}</p>
        <p><strong>Usuario:</strong> {pedido.usuario.username}</p>
        <p><strong>Teléfono:</strong> {pedido.telefono}</p>
        <p><strong>Dirección:</strong> {pedido.direccion}</p>
        <p><strong>Tipo de compra:</strong> {pedido.get_tipo_compra_display()}</p>
        <p><strong>Pago a crédito:</strong> {"Sí" if pedido.pago_credito else "No"}</p>
        <p><strong>Estado:</strong> {pedido.estado}</p>

        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio unitario</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
    """

    for detalle in detalles:
        html += f"""
                <tr>
                    <td>{detalle.producto.nombre}</td>
                    <td>{detalle.cantidad}</td>
                    <td>${detalle.precio_unitario}</td>
                    <td>${detalle.subtotal}</td>
                </tr>
        """

    html += f"""
            </tbody>
        </table>

        <div class="totales">
            <p><strong>Subtotal:</strong> ${pedido.subtotal_sin_interes}</p>
            <p><strong>Interés aplicado:</strong> ${pedido.interes}</p>
            <h2>Total: ${pedido.total}</h2>
        </div>

        <div class="nota">
            <p>Documento generado automáticamente por el sistema Innova Food.</p>
        </div>
    </body>
    </html>
    """

    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = f'attachment; filename="factura_pedido_{pedido.id}.html"'
    return response

# =====================================================
# FACTURA PDF - INNOVA FOOD
# Esta función reemplaza la descarga HTML anterior.
# Al estar al final del archivo, Django usará esta versión.
# =====================================================
@login_required
@user_passes_test(es_admin)
def descargar_factura(request, pedido_id):
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch

    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()

    buffer = BytesIO()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="factura_pedido_{pedido.id}.pdf"'

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "TituloInnova",
        parent=styles["Title"],
        textColor=colors.HexColor("#1faa59"),
        fontSize=24,
        spaceAfter=12
    )

    subtitulo_style = ParagraphStyle(
        "SubtituloInnova",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#111111"),
        fontSize=14,
        spaceAfter=12
    )

    normal_style = styles["Normal"]

    elementos = []

    elementos.append(Paragraph("INNOVA FOOD", titulo_style))
    elementos.append(Paragraph("Factura / Comprobante de pedido", subtitulo_style))
    elementos.append(Spacer(1, 12))

    datos_cliente = f"""
    <b>Pedido:</b> #{pedido.id}<br/>
    <b>Fecha:</b> {pedido.fecha.strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Cliente:</b> {pedido.nombre_cliente}<br/>
    <b>Usuario:</b> {pedido.usuario.username}<br/>
    <b>Teléfono:</b> {pedido.telefono}<br/>
    <b>Dirección:</b> {pedido.direccion}<br/>
    <b>Tipo de compra:</b> {pedido.get_tipo_compra_display()}<br/>
    <b>Pago a crédito:</b> {"Sí" if pedido.pago_credito else "No"}<br/>
    <b>Estado:</b> {pedido.estado}
    """

    elementos.append(Paragraph(datos_cliente, normal_style))
    elementos.append(Spacer(1, 18))

    data = [
        ["Producto", "Cantidad", "Precio unitario", "Subtotal"]
    ]

    for detalle in detalles:
        data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario}",
            f"${detalle.subtotal}",
        ])

    tabla = Table(
        data,
        colWidths=[2.7 * inch, 1.0 * inch, 1.4 * inch, 1.2 * inch]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1faa59")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f7f7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 18))

    totales = f"""
    <para alignment="right">
    <b>Subtotal:</b> ${pedido.subtotal_sin_interes}<br/>
    <b>Interés aplicado:</b> ${pedido.interes}<br/>
    <b>Total:</b> ${pedido.total}
    </para>
    """

    elementos.append(Paragraph(totales, normal_style))
    elementos.append(Spacer(1, 20))

    nota = """
    <b>Nota:</b> Documento generado automáticamente por el sistema Innova Food.
    Esta factura sirve como comprobante interno del pedido realizado.
    """

    elementos.append(Paragraph(nota, normal_style))

    doc.build(elementos)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response
