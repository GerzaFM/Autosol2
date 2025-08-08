import sqlite3
conn = sqlite3.connect('facturas.db')
c = conn.cursor()

print("=== BUSCANDO DUPLICADOS DE HB SYSTEM'S ===")

# Buscar TODOS los proveedores con RFC HSY111130KW4
c.execute("SELECT id, nombre, rfc, nombre_en_quiter FROM proveedor WHERE rfc='HSY111130KW4'")
proveedores_hb = c.fetchall()
print(f"Proveedores con RFC HSY111130KW4: {len(proveedores_hb)}")
for p in proveedores_hb:
    print(f"  ID {p[0]}: nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}'")

# Buscar proveedores con nombre similar a HB
c.execute("SELECT id, nombre, rfc, nombre_en_quiter FROM proveedor WHERE nombre LIKE '%HB%' OR nombre LIKE '%SYSTEM%'")
proveedores_similares = c.fetchall()
print(f"\nProveedores con nombre similar a HB/SYSTEM: {len(proveedores_similares)}")
for p in proveedores_similares:
    print(f"  ID {p[0]}: nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}'")

# Ver los últimos proveedores creados
c.execute("SELECT id, nombre, rfc, nombre_en_quiter FROM proveedor ORDER BY id DESC LIMIT 10")
print(f"\nÚltimos 10 proveedores creados:")
for p in c.fetchall():
    print(f"  ID {p[0]}: nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}'")

conn.close()
