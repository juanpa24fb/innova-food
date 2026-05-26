from django import forms
from django.contrib.auth.models import User
from .models import Producto, Pedido, DatosPago


class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmar contraseña"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        labels = {
            "username": "Usuario",
            "email": "Correo electrónico",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "cantidad_presentacion",
            "unidad_medida",
            "stock",
            "disponible",
            "imagen",
        ]
        labels = {
            "nombre": "Nombre del producto",
            "descripcion": "Descripción",
            "precio": "Precio por presentación",
            "cantidad_presentacion": "Cantidad de presentación",
            "unidad_medida": "Unidad de medida",
            "stock": "Stock disponible",
            "disponible": "Producto disponible",
            "imagen": "Imagen del producto",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ejemplo: Leche"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Ejemplo: 0.60"}),
            "cantidad_presentacion": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Ejemplo: 500"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "disponible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class DatosPagoForm(forms.ModelForm):
    class Meta:
        model = DatosPago
        fields = [
            "banco",
            "tipo_cuenta",
            "numero_cuenta",
            "titular",
            "identificacion",
            "correo",
            "whatsapp",
            "mensaje_whatsapp",
            "nota",
        ]
        widgets = {
            "banco": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ejemplo: Banco Pichincha"}),
            "tipo_cuenta": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ahorros o Corriente"}),
            "numero_cuenta": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de cuenta"}),
            "titular": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del titular"}),
            "identificacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula o RUC"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo del titular"}),
            "whatsapp": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ejemplo: 593999999999"}),
            "mensaje_whatsapp": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "nota": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Instrucciones adicionales para el pago"}),
        }


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["nombre_cliente", "telefono", "direccion", "tipo_compra", "pago_credito"]
        labels = {
            "nombre_cliente": "Nombre completo",
            "telefono": "Teléfono",
            "direccion": "Dirección de entrega o retiro",
            "tipo_compra": "Tipo de compra",
            "pago_credito": "Deseo pagar a crédito si aplica",
        }
        widgets = {
            "nombre_cliente": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de teléfono"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dirección para envío o retiro"}),
            "tipo_compra": forms.Select(attrs={"class": "form-control"}),
            "pago_credito": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["comprobante"]
        widgets = {
            "comprobante": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
