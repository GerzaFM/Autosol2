import sqlite3

conn = sqlite3.connect("facturas.db")
cursor = conn.cursor()

print("=== VERIFICANDO CAMPO CUENTA_MAYOR EN FACTURA ===")
cursor.execute("PRAGMA table_info(factura)")
columns = cursor.fetchall()

cuenta_mayor_exists = False
for col in columns:
    if col[1] == 'cuenta_mayor':
        cuenta_mayor_exists = True
        print(f"✅ Campo cuenta_mayor: {col[2]}")
        break

if not cuenta_mayor_exists:
    print("❌ Campo cuenta_mayor NO existe")
    print("Agregando campo cuenta_mayor...")
    cursor.execute("ALTER TABLE factura ADD COLUMN cuenta_mayor INTEGER")
    conn.commit()
    print("✅ Campo cuenta_mayor agregado")
else:
    print("✅ Campo cuenta_mayor ya existe")

conn.close()
print("Verificación completada")
