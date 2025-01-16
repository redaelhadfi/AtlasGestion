import os
from django.contrib.auth.models import User
from django.db import models
from PIL import Image as PilImage
from django.core.files.base import ContentFile
import io
from django.utils.timezone import now
import uuid
import re
from django.core.exceptions import ValidationError
from django.db.models import Q, UniqueConstraint

from app.utils import normalizar_rut

class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="provincias")

    class Meta:
        unique_together = ("nombre", "region")

    def __str__(self):
        return f"{self.nombre} - {self.region.nombre}"


class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="comunas")

    class Meta:
        unique_together = ("nombre", "provincia") 

    def __str__(self):
        return f"{self.nombre} - {self.provincia.nombre}, {self.provincia.region.nombre}"

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, related_name="ciudades")

    class Meta:
        unique_together = ("nombre", "comuna") 

    def __str__(self):
        return f"{self.nombre} - {self.comuna.nombre}, {self.comuna.provincia.region.nombre}"


class Membresia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    val_mensual = models.IntegerField(null=True, blank=True, verbose_name="Valor mensual")
    val_adicional = models.IntegerField(null=True, blank=True, verbose_name="Valor adicional")
    duracion_dias = models.PositiveIntegerField(verbose_name="Duración (días)")
    max_users = models.PositiveIntegerField(verbose_name="Usuarios máximos permitidos")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción")

    def __str__(self):
        return f"{self.nombre} - Máx. {self.max_users} usuarios"


class Negocio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255) #Raz. social
    rut_empresa = models.CharField(max_length=12, unique=True)
    giro = models.CharField(max_length=255, null=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_mayorista = models.BooleanField(default=False, verbose_name='¿Es Mayorista?')
    #logo = models.ImageField(upload_to='negocios_logos/', blank=True, null=True)  # Campo de imagen
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name="negocios")
    provincia = models.ForeignKey(Provincia, on_delete=models.SET_NULL, null=True, related_name="negocios")
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, related_name="negocios")
    fono_contacto = models.CharField(max_length=20)
    correo = models.CharField(max_length=50)
    membresia = models.ForeignKey(Membresia, on_delete=models.SET_NULL, null=True, blank=True, related_name="negocios")

    def usuarios_activos(self):
        return self.staff.filter(user__is_active=True).count()

    def puede_agregar_usuario(self):
        if not self.membresia:
            return False  
        return self.usuarios_activos() < self.membresia.max_users
    
    def save(self, *args, **kwargs):
        # Normalizar el RUT antes de guardar
        if self.rut_empresa:
            self.rut_empresa = normalizar_rut(self.rut_empresa)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.nombre

    
class Almacen(models.Model):
    id = models.AutoField(primary_key=True)
    direccion = models.CharField(max_length=255)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE) 

    def __str__(self):
        return f'Almacén en {self.direccion}'

class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut_empresa = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name="proveedores")
    provincia = models.ForeignKey(Provincia, on_delete=models.SET_NULL, null=True, related_name="proveedores")
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, related_name="proveedores")
    correo = models.CharField(max_length=50)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'negocio'], name='unique_proveedor_negocio')  
        ]

    def save(self, *args, **kwargs):
        # Normalizar el RUT antes de guardar
        if self.rut_empresa:
            self.rut_empresa = normalizar_rut(self.rut_empresa)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre

    
class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='categorias') 

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'negocio'], name='unique_categoria_negocio')  
        ]
        
    def __str__(self):
        return self.nombre
    
class Marca(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='marcas')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'negocio'], name='unique_marca_negocio')  
        ]

    def __str__(self):
        return self.nombre

class TipoProducto(models.Model):
    TIPO_CLASIFICACION_CHOICES = [
        ('unidad', 'Unidad de Medida'),    # Para litros, cm, kg, etc.
        ('talla', 'Talla de Ropa'),        # Para S, M, L, XL, etc.
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_CLASIFICACION_CHOICES)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"

class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.ForeignKey('TipoProducto', on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(null=True, blank=True, default=0)
    precio_mayorista = models.IntegerField(null=True, blank=True, default=0)  
    descuento = models.IntegerField(null=True, blank=True, default=0)
    descuento_mayorista = models.IntegerField(null=True, blank=True, default=0)
    stock = models.IntegerField(default=0)
    almacen = models.ForeignKey('Almacen', on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('registrado_reciente', 'Registrado Reciente'),
        ('disponible', 'Disponible'),
        ('sin_stock', 'Sin Stock'),
        ('ingresado_manual', 'Ingresado Manual')
    ], default='registrado_reciente')
    is_variable = models.BooleanField(default=False)  

    # Campos relacionados con ILA
    TASA_ILA_CHOICES = [
        (0, 'No aplica'),
        (10, 'Bebidas analcohólicas (10%)'),
        (18, 'Bebidas analcohólicas con alto contenido de azúcar (18%)'),
        (21, 'Vinos, chichas, sidras y cervezas (20.5%)'),
        (32, 'Licores, piscos, whisky y destilados (31.5%)'),
        (53, 'Cigarros puros (52.6%)'),
        (60, 'Tabaco elaborado (59.7%)'),
        (30, 'Cigarrillos (30% + impuesto específico)'),
    ]
    tasa_ila = models.IntegerField(
        choices=TASA_ILA_CHOICES,
        default=0,
        verbose_name='Tasa del Impuesto ILA'
    )

    precio_ila_diferencia = models.IntegerField(null=True, blank=True) 
    precio_mayorista_ila_diferencia = models.IntegerField(null=True, blank=True) 

    def calcular_ila_diferencia(self):
        if self.precio is not None and self.tasa_ila is not None:
            tasa_factor = 1 + (self.tasa_ila / 100)
            precio_sin_ila = self.precio / tasa_factor
            ila_diferencia = self.precio - precio_sin_ila
            self.precio_ila_diferencia = round(ila_diferencia)

        if self.precio_mayorista is not None and self.tasa_ila is not None:
            tasa_factor = 1 + (self.tasa_ila / 100)
            precio_mayorista_sin_ila = self.precio_mayorista / tasa_factor
            ila_mayorista_diferencia = self.precio_mayorista - precio_mayorista_sin_ila
            self.precio_mayorista_ila_diferencia = round(ila_mayorista_diferencia)
    
    iva_precio = models.IntegerField(default=19, verbose_name="IVA Precio (%)")
    iva_precio_mayorista = models.IntegerField(default=19, verbose_name="IVA Precio Mayorista (%)")

    def calcular_iva(self):
        if self.precio:
            tasa_base = 1 + (self.iva_precio / 100)
            return round(self.precio - (self.precio / tasa_base))
        return 0

    def calcular_iva_mayorista(self):
        if self.precio_mayorista:
            tasa_base = 1 + (self.iva_precio_mayorista / 100)
            return round(self.precio_mayorista - (self.precio_mayorista / tasa_base))
        return 0
    
    def actualizar_estado(self):
        if self.stock <= 0:
            self.estado = 'sin_stock'
        else:
            self.estado = 'disponible'
        self.save()

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = str(uuid.uuid4())[:8].upper()

        self.calcular_ila_diferencia()
        
        # Solo forzar a 0 si el precio no ha sido explícitamente modificado
        if self.is_variable and not self.precio:
            self.precio = 0


        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.nombre

class ProductoRopa(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='ropa')
    nombre_talla = models.CharField(
        max_length=10,
        choices=[
            ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'),
            ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')
        ],
        null=True, blank=True  
    )
    unidades = models.IntegerField(default=0, null=True, blank=True)
    id_seg = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Campo adicional para segmentar las tallas registradas - id segmentado

    class Meta:
        unique_together = ('producto', 'nombre_talla')

    def save(self, *args, **kwargs):
        # Generar un identificador único si no existe
        if not self.id_seg:
            self.id_seg = f"{self.producto_id}-{self.nombre_talla}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_talla} - {self.producto.nombre}"

class ProductoUnidades(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='unidades_producto')
    unidades = models.IntegerField(default=1, null=True, blank=True)

class ProductoVariable(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='variable')
    TIPO_PESO_CHOICES = [
        ('gr', 'Gramos'),
        ('kl', 'Kilogramos'),
        ('lt', 'Litros')
    ]
    tipo_peso = models.CharField(max_length=2, choices=TIPO_PESO_CHOICES, null=True, blank=True)
    gr_o_lt = models.FloatField(null=True, blank=True)
    cantidad = models.FloatField(null=True, blank=True)
    precio_venta = models.IntegerField(null=True, blank=True, default=0)
    vendido = models.BooleanField(default=False)
    
    def revertir_venta(self):
        """Revertir la venta si se cancela."""
        self.delete()

class EntradaBodega(models.Model):
    id = models.AutoField(primary_key=True)
    numero_factura = models.CharField(max_length=50, unique=True)  
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)  
    fecha_recepcion = models.DateField() 
    orden_compra = models.CharField(max_length=50, blank=True, null=True)  
    forma_pago = models.CharField(max_length=20, choices=[
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
        ('tbc', 'TBC')
    ])  
    bodega = models.ForeignKey('Almacen', on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.proveedor.nombre}"

class EntradaBodegaProducto(models.Model):
    entrada_bodega = models.ForeignKey(EntradaBodega, on_delete=models.CASCADE, related_name="productos")  
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE) 
    cantidad_recibida = models.PositiveIntegerField()  
    precio_total = models.IntegerField(default=0)
    precio_neto = models.IntegerField(default=0)
    iva_compra = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.cantidad_recibida}x {self.producto.nombre} - {self.entrada_bodega.numero_factura}"

class ProductosDevueltos(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="devoluciones")
    entrada_bodega = models.ForeignKey(EntradaBodega, on_delete=models.CASCADE, related_name="devoluciones")  # Relación con la entrada original
    cantidad_devuelta = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    motivo_devolucion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Productos Devueltos"

    def __str__(self):
        return f"Devolución de {self.cantidad_devuelta} unidades de {self.producto.nombre} - Factura {self.numero_factura}"

    @property
    def numero_factura(self):
        
        return self.entrada_bodega.numero_factura


class PerfilClienteEmpresa(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    raz_social = models.CharField(max_length=255, null=True, blank=True)
    giro = models.CharField(max_length=255, null=True, blank=True)
    
    rut_empresa = models.CharField(max_length=12, null=True, blank=True, unique=False)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="perfilClienteEmpresa")
    provincia = models.ForeignKey(Provincia, on_delete=models.SET_NULL, null=True, blank=True, related_name="perfilClienteEmpresa")
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True, related_name="perfilClienteEmpresa")
    
    correo = models.EmailField(max_length=255, null=True, blank=True, unique=False)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    
    linea_credito = models.IntegerField(default=0)
    descuento_fijo = models.IntegerField(default=0)
    dias_pago = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre or "Empresa sin nombre"} - {self.rut_empresa or "Sin RUT"}'


class PerfilClientes(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    rut = models.CharField(max_length=12, null=True, blank=True, unique=False)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    comuna = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    correo = models.EmailField(max_length=255, null=True, blank=True, unique=False)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    linea_credito = models.IntegerField(default=0)
    descuento_fijo = models.IntegerField(default=0)
    dias_pago = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.nombre or "Cliente sin nombre"} - {self.rut or "Sin RUT"}'


class Carrito(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='CarritoProducto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    tipo = models.CharField(max_length=10, choices=[('boleta', 'Boleta'), ('factura', 'Factura')])
    
    def actualizar_total(self):
        subtotal = 0
        descuento_total = 0

        for item in self.carritoproducto_set.all():

            precio_sin_iva = item.producto.precio / 1.19

            descuento = (item.producto.descuento or 0) / 100
            precio_con_descuento = precio_sin_iva * (1 - descuento)

            subtotal += precio_con_descuento * item.cantidad

            descuento_total += (precio_sin_iva * descuento) * item.cantidad

        subtotal_con_descuento = subtotal - descuento_total
        iva_total = subtotal_con_descuento * 0.19
        total = subtotal_con_descuento + iva_total

        self.subtotal = round(subtotal)  
        self.descuento_total = round(descuento_total) 
        self.iva_total = round(iva_total)  
        self.total = round(total)  
        self.save()

    def actualizar_total_mayorista(self):
        subtotal = 0
        descuento_total = 0

        for item in self.carritoproducto_set.all():
            
            precio_sin_iva = item.producto.precio_mayorista / 1.19
            
            descuento = (item.producto.descuento_mayorista or 0) / 100
            precio_con_descuento = precio_sin_iva * (1 - descuento)


            subtotal += precio_con_descuento * item.cantidad


            descuento_total += (precio_sin_iva * descuento) * item.cantidad


        subtotal_con_descuento = subtotal - descuento_total
        iva_total = subtotal_con_descuento * 0.19
        total = subtotal_con_descuento + iva_total


        self.subtotal = round(subtotal) 
        self.descuento_total = round(descuento_total)  
        self.iva_total = round(iva_total)
        self.total = round(total) 
        self.save()




class CarritoProducto(models.Model):
    id = models.AutoField(primary_key=True)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.IntegerField()  

    def total_precio(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}' 
    
    def total_precio(self):
        if self.carrito.tipo == "factura":
            return self.cantidad * self.producto.precio_mayorista
        else:
            return self.cantidad * self.producto.precio

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'
########################################
####INTEGRACIÓN SII MODELOS Y CAMPOS####
########################################
class Compra(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('boleta', 'Boleta'),
        ('factura', 'Factura'),
    ]
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='boleta',
        verbose_name="Tipo de Documento"
    )
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()
    correo = models.EmailField(null=True, blank=True)
    nombre_staff = models.CharField(max_length=255, null=True, blank=True)
    medio_pago = models.CharField(max_length=20, choices=[
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito o Débito'),
        ('efectivo', 'Efectivo')
    ], default='efectivo')
    glosa = models.TextField(null=True, blank=True)
    subtotal = models.IntegerField(default=0)
    descuento_total = models.IntegerField(default=0)
    iva_total = models.IntegerField(default=0)

    # Nuevos campos añadidos
    negocio = models.ForeignKey('Negocio', on_delete=models.CASCADE, related_name="compras")  # Emisor
    cliente_natural = models.ForeignKey(PerfilClientes, on_delete=models.SET_NULL, null=True, blank=True)  # Receptor (cliente natural)
    cliente_empresa = models.ForeignKey(PerfilClienteEmpresa, on_delete=models.SET_NULL, null=True, blank=True)  # Receptor (empresa)
    folio = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f'Compra #{self.folio or self.id} - {self.usuario}'

    def calcular_totales(self):
        subtotal = sum(detalle.subtotal() for detalle in self.detalles.all())
        iva = subtotal * 0.19
        total = subtotal + iva
        self.subtotal = round(subtotal)
        self.iva_total = round(iva)
        self.total = round(total)
        self.save()


class DetalleCompra(models.Model):
    id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.IntegerField()  

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
            return f'{self.cantidad} x {self.producto.nombre} en Compra {self.compra.folio or self.compra.id}'

class Referencia(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="referencias")
    numero_linea = models.PositiveIntegerField()
    tipo_documento_ref = models.CharField(max_length=50)
    folio_referencia = models.CharField(max_length=50)
    fecha_referencia = models.DateField()
    razon_referencia = models.TextField()

    def __str__(self):
        return f"Referencia {self.tipo_documento_ref} - Folio {self.folio_referencia}"

class Totales(models.Model):
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name="totales")
    monto_neto = models.IntegerField()
    tasa_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.0)
    iva = models.IntegerField()
    monto_total = models.IntegerField()

    def __str__(self):
        return f"Totales Compra {self.compra.folio or self.compra.id}"

class TimbreElectronicoDigital(models.Model):
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name="ted")
    rut_emisor = models.CharField(max_length=12)
    tipo_dte = models.CharField(max_length=10)
    folio = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    rut_receptor = models.CharField(max_length=12)
    razon_social_receptor = models.CharField(max_length=255)
    monto_total = models.IntegerField()
    item_principal = models.CharField(max_length=255)
    timestamp_ted = models.DateTimeField()
    algoritmo_firma = models.CharField(max_length=50)
    firma = models.TextField()

    def __str__(self):
        return f"TED Compra {self.compra.folio or self.compra.id}"

########################################
####INTEGRACIÓN SII MODELOS Y CAMPOS####
########################################

class StaffProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, default='Activo')
    negocio = models.ForeignKey('Negocio', on_delete=models.CASCADE, related_name='staff')

    def save(self, *args, **kwargs):
        # Normalizar el RUT antes de guardar
        self.rut = normalizar_rut(self.rut)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.negocio.nombre}"


#MODELOS DE AUDITORIA
class HistorialProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cambio = models.TextField()
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.producto.nombre} modificado por {self.usuario.username}'

class HistorialUsuario(models.Model):
    usuario_modificado = models.ForeignKey(User, related_name='usuario_modificado', on_delete=models.CASCADE)
    usuario_accion = models.ForeignKey(User, related_name='usuario_accion', on_delete=models.SET_NULL, null=True)
    cambio = models.TextField()
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Usuario {self.usuario_modificado.username} modificado por {self.usuario_accion.username}'

class RegistroErrores(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ruta = models.CharField(max_length=255)
    metodo = models.CharField(max_length=10)
    error = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Error en {self.ruta} por {self.usuario.username if self.usuario else 'desconocido'}"