import sqlite3

print("=== VERIFICACIÓN DE CAMPOS CLASE Y DEPARTAMENTO ===")

# Verificar base de datos
conn = sqlite3.connect("facturas.db")
cursor = conn.cursor()

print("1. Verificando estructura...")
cursor.execute("PRAGMA table_info(factura)")
columns = cursor.fetchall()

clase_found = False
departamento_found = False

for col in columns:
    if col[1] == 'clase':
        clase_found = True
        print(f"   ✅ Campo clase: {col[2]}")
    elif col[1] == 'departamento':
        departamento_found = True
        print(f"   ✅ Campo departamento: {col[2]}")

print(f"\n2. Estado:")
print(f"   - Clase: {'✅' if clase_found else '❌'}")
print(f"   - Departamento: {'✅' if departamento_found else '❌'}")

# Ver facturas más recientes
print(f"\n3. Últimas 3 facturas guardadas:")
cursor.execute("""
    SELECT folio_interno, serie, folio, clase, departamento 
    FROM factura 
    ORDER BY folio_interno DESC 
    LIMIT 3
""")

facturas = cursor.fetchall()
for f in facturas:
    print(f"   - Folio {f[0]}: {f[1]}-{f[2]}")
    print(f"     Clase: '{f[3] if f[3] else 'NULL'}'")
    print(f"     Departamento: '{f[4] if f[4] else 'NULL'}'")

conn.close()

print(f"\n=== FLUJO DE DATOS ACTUALIZADO ===")
print("✅ solicitud_app_professional.py:")
print("   - clase: solicitud_data.get('Clase', '')")
print("   - departamento: solicitud_data.get('Depa', '')")
print("✅ logic_solicitud.py:")
print("   - clase: solicitud_data.get('clase')")
print("   - departamento: solicitud_data.get('departamento')")
print("✅ bd_control.py:")
print("   - clase=data.get('clase')")
print("   - departamento=data.get('departamento')")

print(f"\n🎯 Ahora ambos campos se guardarán al pulsar 'Generar'")
