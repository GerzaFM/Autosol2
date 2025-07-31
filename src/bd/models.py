from peewee import SqliteDatabase, Model, CharField, DateField, DecimalField, ForeignKeyField, IntegerField, AutoField, BooleanField
import os

# Configurar la ruta absoluta a la base de datos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
db_path = os.path.join(project_root, "facturas.db")

db = SqliteDatabase(db_path)

class Proveedor(Model):
    id = IntegerField(primary_key=True)  # Primary key autoincremental
    nombre = CharField()
    rfc = CharField(unique=True)
    telefono = CharField(null=True)
    email = CharField(null=True)
    nombre_contacto = CharField(null=True)
    codigo_quiter = IntegerField(null=True)

    class Meta:
        database = db


class Layout(Model):
    id = IntegerField(primary_key=True)
    nombre = CharField()
    fecha = DateField()

    class Meta:
        database = db


class Factura(Model):
    folio_interno = IntegerField(primary_key=True)
    serie = CharField()  # Cambiado de IntegerField a CharField para manejar "CC", "OLEK", etc.
    folio = IntegerField()
    fecha = DateField()
    fecha_emision = DateField()
    tipo = CharField()
    nombre_emisor = CharField()
    rfc_emisor = CharField()
    nombre_receptor = CharField()
    rfc_receptor = CharField()
    subtotal = DecimalField()
    ret_iva = DecimalField(null=True)
    ret_isr = DecimalField(null=True)
    iva_trasladado = DecimalField(null=True)
    total = DecimalField()
    comentario = CharField(null=True)
    clase = CharField(null=True)  # Campo opcional para la clase de factura
    proveedor = ForeignKeyField(Proveedor, backref='facturas')
    layout = ForeignKeyField(Layout, backref='facturas', null=True)
    cargada = BooleanField(default=False)
    pagada = BooleanField(default=False)
    
    class Meta:
        database = db
        indexes = (
            (('proveedor', 'serie', 'folio'), True),  # Sin espacio extra
        )


class Concepto(Model):
    id = IntegerField(primary_key=True)
    descripcion = CharField()
    cantidad = DecimalField()
    precio_unitario = DecimalField()
    total = DecimalField()
    factura = ForeignKeyField(Factura, backref='conceptos')

    class Meta:
        database = db

class Reparto(Model):
    id = IntegerField(primary_key=True)
    comercial = DecimalField(null=True)
    fleet = DecimalField(null=True)
    seminuevos = DecimalField(null=True)
    refacciones = DecimalField(null=True)
    servicio = DecimalField(null=True)
    hyp = DecimalField(null=True)
    administracion = DecimalField(null=True)
    factura = ForeignKeyField(Factura, backref='reparto', unique=True, null=True)  # Relación uno a uno

    class Meta:
        database = db

class Vale(Model):
    id = IntegerField(primary_key=True)  # Primary key autoincremental
    noVale = CharField(unique=True)  # Único pero no primary key
    tipo = CharField()
    noDocumento = CharField()
    descripcion = CharField()
    referencia = IntegerField()
    total = CharField()
    cuenta = IntegerField(null=True) 
    fechaVale = DateField(null=True)
    departamento = IntegerField(null=True) 
    sucursal = IntegerField(null=True)
    marca = IntegerField(null=True)
    responsable = IntegerField(null=True)
    proveedor = CharField(null=True)
    codigo = CharField(null=True)  # Código del proveedor extraído del vale
    factura = ForeignKeyField(Factura, backref='vale', unique=True, null=True, db_column='factura')  # Relación uno a uno con factura

    class Meta:
        database = db

class OrdenCompra(Model):
    id = IntegerField(primary_key=True)
    factura = ForeignKeyField(Factura, backref='ordenes_compra', null=True)
    cuenta = IntegerField()  # Cuenta del proveedor
    nombre = CharField()  # Nombre del proveedor
    referencia = IntegerField()  # Campo legacy requerido (referencia)
    fecha = DateField()  # Campo legacy requerido (fecha)
    importe = DecimalField()  # Importe de la orden
    importe_en_letras = CharField()  # Importe en letras
    iva = DecimalField(null=True)  # Campo legacy opcional
    cuenta_mayor = IntegerField(null=True)  # Campo legacy opcional
    ref_movimiento = CharField(null=True)  # Referencia del movimiento (nuevo)
    codigo_banco = CharField(null=True)  # Código del banco (ej: BTC23)
    folio_factura = CharField(null=True)  # Folio de la factura extraído
    archivo_original = CharField(null=True)  # Nombre del archivo PDF original
    fecha_procesamiento = DateField(null=True)  # Fecha cuando se procesó

    class Meta:
        database = db

class Banco(Model):
    id = IntegerField(primary_key=True)
    nombre = CharField()
    cuenta = CharField(unique=True)
    codigo = CharField(unique=True)

    class Meta:
        database = db

class Usuario(Model):
    codigo = IntegerField(primary_key=True)
    nombre = CharField()
    empresa = IntegerField()
    centro = IntegerField()
    sucursal = IntegerField()
    marca = IntegerField()
    email = CharField(null=True)
    permisos = CharField(null=True)
    responsable = ForeignKeyField('self', null=True, backref='subordinados')

    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = db

class RepartoFavorito(Model):
    usuario = ForeignKeyField(Usuario, backref='repartos_favoritos')
    nombre_personalizado = CharField()  # Nombre que aparecerá en el botón
    comercial = DecimalField(null=True)
    fleet = DecimalField(null=True)
    seminuevos = DecimalField(null=True)
    refacciones = DecimalField(null=True)
    servicio = DecimalField(null=True)
    hyp = DecimalField(null=True)
    administracion = DecimalField(null=True)
    posicion = IntegerField()  # Para saber qué botón es (0-4)

    class Meta:
        database = db
        indexes = (
            (('usuario', 'posicion'), True),  # Un usuario no puede tener dos favoritos en la misma posición
        )

