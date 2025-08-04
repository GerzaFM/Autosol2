import sqlite3
import os

db_path = "facturas.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== VERIFICANDO TABLA FACTURA ===")
cursor.execute("PRAGMA table_info(factura)")
columns = cursor.fetchall()

departamento_exists = False
clase_exists = False

print("Campos en tabla factura:")
for col in columns:
    campo = col[1]
    tipo = col[2]
    print(f"  {campo}: {tipo}")
    
    if campo == 'departamento':
        departamento_exists = True
    if campo == 'clase':
        clase_exists = True

print(f"\nEstado de campos:")
print(f"  clase: {'✅' if clase_exists else '❌'}")
print(f"  departamento: {'✅' if departamento_exists else '❌'}")

if not departamento_exists:
    print("\nAgregando campo departamento...")
    try:
        cursor.execute("ALTER TABLE factura ADD COLUMN departamento VARCHAR(255)")
        conn.commit()
        print("✅ Campo departamento agregado exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("\n✅ El campo departamento ya existe")

conn.close()
print("\nProceso completado")
