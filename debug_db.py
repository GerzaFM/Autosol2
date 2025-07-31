import sqlite3

# Inspeccionar la base de datos
conn = sqlite3.connect('facturas.db')
cursor = conn.cursor()

print("📋 ÚLTIMOS 5 REPARTOS:")
cursor.execute('SELECT * FROM reparto ORDER BY id DESC LIMIT 5;')
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Factura_ID: {row[8]}, Comercial: {row[1]}, Fleet: {row[2]}")

print("\n📋 ÚLTIMAS 5 FACTURAS:")
cursor.execute('SELECT folio_interno, serie, folio, tipo FROM factura ORDER BY folio_interno DESC LIMIT 5;')
for row in cursor.fetchall():
    print(f"Folio_Interno: {row[0]}, Serie-Folio: {row[1]}-{row[2]}, Tipo: {row[3]}")

print("\n🔍 VERIFICAR RESTRICCIÓN UNIQUE EN REPARTO:")
cursor.execute("PRAGMA table_info(reparto);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]} - {'UNIQUE' if col[5] else 'NO UNIQUE'}")

print("\n🔍 DEFINICIÓN COMPLETA DE LA TABLA REPARTO:")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reparto';")
definition = cursor.fetchone()
if definition:
    print(definition[0])

print("\n🔍 ÍNDICES EN LA TABLA REPARTO:")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='reparto';")
indices = cursor.fetchall()
for idx in indices:
    if idx[0]:  # Some indices might be None
        print(idx[0])

conn.close()
