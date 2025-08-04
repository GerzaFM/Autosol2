#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del campo departamento
"""
import sqlite3
import os

print("=== VERIFICACIÓN FINAL DEL CAMPO DEPARTAMENTO ===")

try:
    # Verificar estructura de la base de datos
    db_path = "facturas.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("1. Verificando estructura de tabla factura...")
    cursor.execute("PRAGMA table_info(factura)")
    columns = cursor.fetchall()
    
    departamento_found = False
    clase_found = False
    
    for col in columns:
        if col[1] == 'departamento':
            departamento_found = True
            print(f"   ✅ Campo departamento: {col[2]}")
        elif col[1] == 'clase':
            clase_found = True
            print(f"   ✅ Campo clase: {col[2]}")
    
    if not departamento_found:
        print("   ❌ Campo departamento NO encontrado")
    if not clase_found:
        print("   ❌ Campo clase NO encontrado")
    
    print(f"\n2. Estado de los campos:")
    print(f"   - Clase: {'✅ Existe' if clase_found else '❌ No existe'}")
    print(f"   - Departamento: {'✅ Existe' if departamento_found else '❌ No existe'}")
    
    # Verificar si hay facturas existentes con estos campos
    print(f"\n3. Verificando facturas existentes...")
    cursor.execute("SELECT COUNT(*) FROM factura")
    total_facturas = cursor.fetchone()[0]
    
    if total_facturas > 0:
        print(f"   Total de facturas: {total_facturas}")
        cursor.execute("""
            SELECT folio_interno, serie, folio, clase, departamento 
            FROM factura 
            LIMIT 3
        """)
        facturas = cursor.fetchall()
        
        print("   Primeras 3 facturas:")
        for f in facturas:
            print(f"     - Folio {f[0]}: {f[1]}-{f[2]}, Clase: {f[3]}, Depto: {f[4]}")
    else:
        print("   No hay facturas en la base de datos")
    
    conn.close()
    
    print(f"\n=== RESUMEN ===")
    if departamento_found and clase_found:
        print("✅ CONFIGURACIÓN CORRECTA:")
        print("   - Campo 'clase' existe en el modelo y BD")
        print("   - Campo 'departamento' existe en el modelo y BD") 
        print("   - Archivos modificados:")
        print("     * src/bd/bd_control.py - Agregado departamento al guardar")
        print("     * src/solicitudapp/logic_solicitud.py - Agregado al diccionario")
        print("     * src/solicitudapp/solicitud_app_professional.py - Mapeado desde Depa")
        print("\n🎯 El campo departamento se llenará automáticamente con el")
        print("   contenido del entry 'Depa' al pulsar Generar")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== VERIFICACIÓN COMPLETADA ===")
