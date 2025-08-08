from src.bd.models import Proveedor

print('=== ÚLTIMOS PROVEEDORES CREADOS ===')
for p in Proveedor.select().order_by(Proveedor.id.desc()).limit(10):
    print(f'ID {p.id}: nombre="{p.nombre}" | nombre_en_quiter="{p.nombre_en_quiter}" | RFC={p.rfc}')

print('\n=== BUSCANDO DUPLICADOS POR NOMBRE ===')
nombres_vistos = {}
for p in Proveedor.select().order_by(Proveedor.id):
    if p.nombre:
        nombre = p.nombre.upper().strip()
        if nombre in nombres_vistos:
            print(f'DUPLICADO: ID {p.id} "{p.nombre}" ya existe como ID {nombres_vistos[nombre]}')
        else:
            nombres_vistos[nombre] = p.id

print('\n=== PROVEEDORES CON NOMBRE_EN_QUITER ===')
count = 0
for p in Proveedor.select().where(Proveedor.nombre_en_quiter.is_null(False)):
    print(f'ID {p.id}: "{p.nombre_en_quiter}"')
    count += 1
    if count > 20:  # Solo mostrar los primeros 20
        print("... (más proveedores)")
        break
