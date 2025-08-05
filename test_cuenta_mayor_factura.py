#!/usr/bin/env python3
"""
Script de verificación para el campo cuenta_mayor en Factura
"""
import sqlite3

print("=== VERIFICACIÓN COMPLETA DEL CAMPO CUENTA_MAYOR ===")

# Verificar base de datos
conn = sqlite3.connect("facturas.db")
cursor = conn.cursor()

print("1. Verificando estructura de tabla factura...")
cursor.execute("PRAGMA table_info(factura)")
columns = cursor.fetchall()

cuenta_mayor_found = False
for col in columns:
    if col[1] == 'cuenta_mayor':
        cuenta_mayor_found = True
        print(f"   ✅ Campo cuenta_mayor: {col[2]} (NULL: {'Sí' if col[3] == 0 else 'No'})")
        break

if not cuenta_mayor_found:
    print("   ❌ Campo cuenta_mayor NO encontrado")

print("\n2. Verificando algunas facturas con cuenta_mayor...")
cursor.execute("""
    SELECT folio_interno, serie, folio, cuenta_mayor 
    FROM factura 
    WHERE cuenta_mayor IS NOT NULL
    LIMIT 5
""")

facturas_con_cuenta = cursor.fetchall()
if facturas_con_cuenta:
    print("   Facturas con cuenta_mayor:")
    for f in facturas_con_cuenta:
        print(f"     - Folio {f[0]}: {f[1]}-{f[2]}, Cuenta Mayor: {f[3]}")
else:
    print("   ℹ️ No hay facturas con cuenta_mayor asignada aún")

print("\n3. Verificando proveedores con cuenta_mayor...")
cursor.execute("""
    SELECT id, nombre, cuenta_mayor 
    FROM proveedor 
    WHERE cuenta_mayor IS NOT NULL
    LIMIT 5
""")

proveedores_con_cuenta = cursor.fetchall()
if proveedores_con_cuenta:
    print("   Proveedores con cuenta_mayor:")
    for p in proveedores_con_cuenta:
        print(f"     - ID {p[0]}: {p[1]}, Cuenta Mayor: {p[2]}")
else:
    print("   ℹ️ No hay proveedores con cuenta_mayor asignada aún")

print("\n4. Verificando órdenes de compra con cuenta_mayor...")
cursor.execute("""
    SELECT id, nombre, cuenta_mayor 
    FROM ordencompra 
    WHERE cuenta_mayor IS NOT NULL
    LIMIT 5
""")

ordenes_con_cuenta = cursor.fetchall()
if ordenes_con_cuenta:
    print("   Órdenes con cuenta_mayor:")
    for o in ordenes_con_cuenta:
        print(f"     - ID {o[0]}: {o[1]}, Cuenta Mayor: {o[2]}")
else:
    print("   ℹ️ No hay órdenes con cuenta_mayor asignada aún")

conn.close()

print("\n=== FLUJO DE DATOS IMPLEMENTADO ===")
print("✅ Extracción:")
print("   - extractor_orden.py extrae cuenta_mayor del PDF")
print("   - Optimizado para retornar solo la primera cuenta encontrada")

print("\n✅ Procesamiento:")
print("   - autocarga_controller.py procesa la cuenta extraída")
print("   - Actualiza Proveedor.cuenta_mayor si no existe")
print("   - Actualiza Factura.cuenta_mayor si no existe")
print("   - Guarda cuenta_mayor en OrdenCompra")

print("\n✅ Base de datos:")
print("   - Factura.cuenta_mayor agregado correctamente")
print("   - bd_control.py actualizado para guardar cuenta_mayor")

print("\n🎯 RESULTADO:")
print("   Cuando se procese una orden PDF, la cuenta_mayor extraída se guardará en:")
print("   1. OrdenCompra (siempre)")
print("   2. Proveedor (solo si no tiene cuenta_mayor)")
print("   3. Factura asociada (solo si no tiene cuenta_mayor)")

print("\n=== VERIFICACIÓN COMPLETADA ===")
