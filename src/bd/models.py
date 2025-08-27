"""
Modelos de base de datos usando Peewee ORM.
Soporta SQLite y PostgreSQL.
"""

from peewee import (
    Model, CharField, DateField, DecimalField, 
    ForeignKeyField, IntegerField, AutoField, 
    BooleanField, TextField, BigIntegerField
)
import os
import logging

# Importar la conexión de base de datos
from .database import db

logger = logging.getLogger(__name__)

class Proveedor(Model):
    """Modelo de proveedores."""
    id = AutoField()
    codigo_quiter = BigIntegerField(null=True)
    nombre = CharField(max_length=255, null=True)
    nombre_en_quiter = CharField(max_length=255, null=True)
    rfc = CharField(max_length=13, null=True)  # RFC máximo 13 caracteres
    telefono = CharField(max_length=20, null=True)
    email = CharField(max_length=100, null=True)
    nombre_contacto = CharField(max_length=255, null=True)
    cuenta_mayor = BigIntegerField(null=True)
    
    class Meta:
        database = db
        table_name = 'proveedores'


class Layout(Model):
    """Modelo de layouts."""
    id = AutoField()
    fecha = DateField()
    nombre = CharField(max_length=255)
    monto = DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        database = db
        table_name = 'layouts'

class Cheque(Model):
    """Modelo de cheques."""
    id = AutoField()
    fecha = DateField()
    vale = CharField(max_length=50)
    folio = CharField(max_length=50)
    proveedor = ForeignKeyField(Proveedor, backref='cheques', null=True, column_name='proveedor_id')
    monto = DecimalField(max_digits=15, decimal_places=2)
    banco = CharField(max_length=100)
    layout = ForeignKeyField(Layout, backref='cheques', null=True, column_name='layout_id')

    class Meta:
        database = db
        table_name = 'cheques'

class Factura(Model):
    """Modelo de facturas."""
    folio_interno = AutoField()
    serie = CharField(max_length=10)
    folio = CharField(max_length=50)
    fecha = DateField()
    fecha_emision = DateField()
    tipo = CharField(max_length=50)
    nombre_emisor = CharField(max_length=255)
    rfc_emisor = CharField(max_length=13)
    nombre_receptor = CharField(max_length=255)
    rfc_receptor = CharField(max_length=13)
    subtotal = DecimalField(max_digits=15, decimal_places=2)
    ret_iva = DecimalField(max_digits=15, decimal_places=2, null=True)
    ret_isr = DecimalField(max_digits=15, decimal_places=2, null=True)
    iva_trasladado = DecimalField(max_digits=15, decimal_places=2, null=True)
    total = DecimalField(max_digits=15, decimal_places=2)
    comentario = TextField(null=True)  # Usar TextField para comentarios largos
    clase = CharField(max_length=50, null=True)
    departamento = CharField(max_length=100, null=True)
    proveedor = ForeignKeyField(Proveedor, backref='facturas', column_name='proveedor_id')
    layout = ForeignKeyField(Layout, backref='facturas', null=True, column_name='layout_id')
    cheque = ForeignKeyField(Cheque, backref='facturas', null=True, column_name='cheque_id')
    cargada = BooleanField(default=False)
    pagada = BooleanField(default=False)
    
    class Meta:
        database = db
        table_name = 'facturas'
        indexes = (
            (('proveedor', 'serie', 'folio'), True),  # Índice único compuesto
        )


class Concepto(Model):
    """Modelo de conceptos de facturas."""
    id = AutoField()
    descripcion = TextField()  # Usar TextField para descripciones largas
    cantidad = DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = DecimalField(max_digits=15, decimal_places=2)
    total = DecimalField(max_digits=15, decimal_places=2)
    factura = ForeignKeyField(Factura, backref='conceptos', column_name='factura_id')

    class Meta:
        database = db
        table_name = 'conceptos'

class Reparto(Model):
    """Modelo de reparto de facturas por departamentos."""
    id = AutoField()
    comercial = DecimalField(max_digits=5, decimal_places=2, null=True)
    fleet = DecimalField(max_digits=5, decimal_places=2, null=True)
    seminuevos = DecimalField(max_digits=5, decimal_places=2, null=True)
    refacciones = DecimalField(max_digits=5, decimal_places=2, null=True)
    servicio = DecimalField(max_digits=5, decimal_places=2, null=True)
    hyp = DecimalField(max_digits=5, decimal_places=2, null=True)
    administracion = DecimalField(max_digits=5, decimal_places=2, null=True)
    factura = ForeignKeyField(Factura, backref='reparto', unique=True, null=True, column_name='factura_id')

    class Meta:
        database = db
        table_name = 'repartos'

class Vale(Model):
    """Modelo de vales."""
    id = AutoField()
    noVale = CharField(max_length=50, unique=True)
    tipo = CharField(max_length=50)
    noDocumento = CharField(max_length=50)
    descripcion = TextField()
    referencia = BigIntegerField()
    total = CharField(max_length=50)  # Mantenido como CharField por compatibilidad
    cuenta = BigIntegerField(null=True) 
    fechaVale = DateField(null=True)
    departamento = IntegerField(null=True) 
    sucursal = IntegerField(null=True)
    marca = IntegerField(null=True)
    responsable = IntegerField(null=True)
    proveedor = CharField(max_length=255, null=True)
    codigo = CharField(max_length=50, null=True)
    factura = ForeignKeyField(Factura, backref='vale', unique=True, null=True, column_name='factura_id')

    class Meta:
        database = db
        table_name = 'vales'

class OrdenCompra(Model):
    """Modelo de órdenes de compra."""
    id = AutoField()
    factura = ForeignKeyField(Factura, backref='ordenes_compra', null=True, column_name='factura_id')
    cuenta = BigIntegerField()
    nombre = CharField(max_length=255)
    referencia = BigIntegerField()
    fecha = DateField()
    importe = DecimalField(max_digits=15, decimal_places=2)
    importe_en_letras = TextField()
    iva = DecimalField(max_digits=15, decimal_places=2, null=True)
    cuenta_mayor = BigIntegerField(null=True)
    ref_movimiento = CharField(max_length=100, null=True)
    codigo_banco = CharField(max_length=10, null=True)
    folio_factura = CharField(max_length=50, null=True)
    archivo_original = CharField(max_length=255, null=True)
    fecha_procesamiento = DateField(null=True)

    class Meta:
        database = db
        table_name = 'ordenes_compra'

class Banco(Model):
    """Modelo de bancos."""
    id = AutoField()
    nombre = CharField(max_length=255)
    cuenta = CharField(max_length=50, unique=True)
    codigo = CharField(max_length=10, unique=True)
    cuenta_mayor = BigIntegerField(null=True)

    class Meta:
        database = db
        table_name = 'bancos'

class Usuario(Model):
    """Modelo de usuarios del sistema."""
    codigo = IntegerField(primary_key=True)
    nombre = CharField(max_length=255)
    empresa = IntegerField()
    centro = IntegerField()
    sucursal = IntegerField()
    marca = IntegerField()
    email = CharField(max_length=100, null=True)
    permisos = CharField(max_length=500, null=True)
    responsable = ForeignKeyField('self', null=True, backref='subordinados', column_name='responsable_id')
    username = CharField(max_length=50, unique=True)
    password = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'usuarios'

class RepartoFavorito(Model):
    """Modelo de repartos favoritos por usuario."""
    usuario = ForeignKeyField(Usuario, backref='repartos_favoritos', column_name='usuario_id')
    nombre_personalizado = CharField(max_length=100)
    comercial = DecimalField(max_digits=5, decimal_places=2, null=True)
    fleet = DecimalField(max_digits=5, decimal_places=2, null=True)
    seminuevos = DecimalField(max_digits=5, decimal_places=2, null=True)
    refacciones = DecimalField(max_digits=5, decimal_places=2, null=True)
    servicio = DecimalField(max_digits=5, decimal_places=2, null=True)
    hyp = DecimalField(max_digits=5, decimal_places=2, null=True)
    administracion = DecimalField(max_digits=5, decimal_places=2, null=True)
    posicion = IntegerField()

    class Meta:
        database = db
        table_name = 'repartos_favoritos'
        indexes = (
            (('usuario', 'posicion'), True),  # Índice único compuesto
        )

# Lista de todos los modelos para facilitar operaciones de migración
ALL_MODELS = [
    Proveedor,
    Layout,
    Cheque,
    Factura,
    Concepto,
    Reparto,
    Vale,
    OrdenCompra,
    Banco,
    Usuario,
    RepartoFavorito
]

