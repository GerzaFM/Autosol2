import sqlite3
from bd.models import db, Proveedor, Factura

# Conectar base de datos
db_path = 'facturas.db'
db.init(db_path)
db.connect()

print("=== FUSIONANDO PROVEEDORES HB ===")

# Buscar los proveedores
proveedor_quiter = Proveedor.get(Proveedor.id == 61)  # HB SYSTEMS S DE RL
proveedor_duplicado = Proveedor.get(Proveedor.id == 113)  # HB SYSTEM'S

print(f"Proveedor Quiter (ID 61): {proveedor_quiter.nombre_en_quiter}")
print(f"Proveedor Duplicado (ID 113): {proveedor_duplicado.nombre} - {proveedor_duplicado.rfc}")

# Actualizar el proveedor de Quiter con los datos del XML
print(f"\n1. Actualizando datos del proveedor ID 61...")
proveedor_quiter.nombre = proveedor_duplicado.nombre
proveedor_quiter.rfc = proveedor_duplicado.rfc
if proveedor_duplicado.telefono:
    proveedor_quiter.telefono = proveedor_duplicado.telefono
if proveedor_duplicado.email:
    proveedor_quiter.email = proveedor_duplicado.email
if proveedor_duplicado.nombre_contacto:
    proveedor_quiter.nombre_contacto = proveedor_duplicado.nombre_contacto
proveedor_quiter.save()
print(f"✅ Proveedor ID 61 actualizado con RFC {proveedor_quiter.rfc}")

# Reasignar facturas del ID 113 al ID 61
print(f"\n2. Reasignando facturas...")
facturas_a_reasignar = Factura.select().where(Factura.proveedor == proveedor_duplicado)
count_facturas = facturas_a_reasignar.count()
print(f"Facturas a reasignar: {count_facturas}")

for factura in facturas_a_reasignar:
    print(f"  - Factura {factura.serie}-{factura.folio}: ID 113 → ID 61")
    factura.proveedor = proveedor_quiter
    factura.save()

# Eliminar el proveedor duplicado
print(f"\n3. Eliminando proveedor duplicado ID 113...")
proveedor_duplicado.delete_instance()
print(f"✅ Proveedor ID 113 eliminado")

print(f"\n=== FUSIÓN COMPLETADA ===")
print(f"Proveedor final (ID 61):")
print(f"  - Nombre: {proveedor_quiter.nombre}")
print(f"  - RFC: {proveedor_quiter.rfc}")
print(f"  - Nombre Quiter: {proveedor_quiter.nombre_en_quiter}")
print(f"  - Código: {proveedor_quiter.codigo_quiter}")
print(f"  - Facturas asociadas: {Factura.select().where(Factura.proveedor == proveedor_quiter).count()}")

db.close()
