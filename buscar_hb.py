import sqlite3
conn = sqlite3.connect('facturas.db')
c = conn.cursor()

print("Buscando facturas de HB SYSTEM'S...")
c.execute("SELECT folio_interno, nombre_emisor, rfc_emisor FROM factura WHERE rfc_emisor='HSY111130KW4'")
facturas = c.fetchall()
print(f"Facturas encontradas: {len(facturas)}")
for f in facturas:
    print(f"  {f[0]}: {f[1]} - {f[2]}")

print("\nBuscando proveedores con nombre parecido a HB...")
c.execute("SELECT id, nombre, rfc, nombre_en_quiter FROM proveedor WHERE nombre LIKE '%HB%' OR nombre_en_quiter LIKE '%HB%'")
proveedores = c.fetchall()
print(f"Proveedores HB: {len(proveedores)}")
for p in proveedores:
    print(f"  ID {p[0]}: nombre='{p[1]}' rfc='{p[2]}' quiter='{p[3]}'")

conn.close()
