import sqlite3

# Conectar base de datos directamente
conn = sqlite3.connect('facturas.db')
c = conn.cursor()

print("=== FUSIONANDO PROVEEDORES HB ===")

# Verificar datos actuales
c.execute('SELECT id, nombre, rfc, nombre_en_quiter, codigo_quiter FROM proveedor WHERE id IN (61, 113)')
proveedores = c.fetchall()
for p in proveedores:
    print(f"ID {p[0]}: nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}' codigo={p[4]}")

# Buscar facturas del ID 113
c.execute('SELECT folio_interno, serie, folio FROM factura WHERE proveedor_id = 113')
facturas_113 = c.fetchall()
print(f"\nFacturas del proveedor ID 113: {len(facturas_113)}")
for f in facturas_113:
    print(f"  - {f[0]}: {f[1]}-{f[2]}")

if len(facturas_113) > 0:
    # Actualizar proveedor ID 61 con datos del ID 113
    print(f"\n1. Actualizando proveedor ID 61 con datos de ID 113...")
    c.execute('''
        UPDATE proveedor 
        SET nombre = (SELECT nombre FROM proveedor WHERE id = 113),
            rfc = (SELECT rfc FROM proveedor WHERE id = 113)
        WHERE id = 61
    ''')
    
    # Reasignar facturas del ID 113 al ID 61
    print(f"2. Reasignando {len(facturas_113)} facturas del ID 113 al ID 61...")
    c.execute('UPDATE factura SET proveedor_id = 61 WHERE proveedor_id = 113')
    
    # Eliminar proveedor ID 113
    print(f"3. Eliminando proveedor duplicado ID 113...")
    c.execute('DELETE FROM proveedor WHERE id = 113')
    
    conn.commit()
    
    # Verificar resultado
    print(f"\n=== FUSIÓN COMPLETADA ===")
    c.execute('SELECT id, nombre, rfc, nombre_en_quiter, codigo_quiter FROM proveedor WHERE id = 61')
    p = c.fetchone()
    print(f"Proveedor final (ID 61): nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}' codigo={p[4]}")
    
    c.execute('SELECT COUNT(*) FROM factura WHERE proveedor_id = 61')
    count_facturas = c.fetchone()[0]
    print(f"Facturas asociadas al ID 61: {count_facturas}")
    
else:
    print("No hay facturas del ID 113 para reasignar")

conn.close()
