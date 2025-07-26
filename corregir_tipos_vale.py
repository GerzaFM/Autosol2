#!/usr/bin/env python3
"""
Script para corregir tipos de vale en la base de datos existente
"""
import sqlite3

def corregir_tipos_vale_bd():
    print("=== CORRIGIENDO TIPOS DE VALE EN BASE DE DATOS ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # Mapeo de tipos incorrectos a tipos correctos
    mapeo_tipos = {
        'VCV': 'VC',  # Vale de Control
        'GUG': 'GU',  # Gasolina
        # Agregar más según se encuentren
    }
    
    correcciones_realizadas = 0
    
    # 1. Ver tipos actuales
    print("\n1. TIPOS ACTUALES EN LA BD:")
    cursor.execute("SELECT DISTINCT tipo FROM vale WHERE tipo IS NOT NULL")
    tipos_actuales = cursor.fetchall()
    for tipo in tipos_actuales:
        print(f"   🏷️ {tipo[0]}")
    
    # 2. Corregir cada tipo incorrecto
    for tipo_incorrecto, tipo_correcto in mapeo_tipos.items():
        # Verificar si existe el tipo incorrecto
        cursor.execute("SELECT COUNT(*) FROM vale WHERE tipo = ?", (tipo_incorrecto,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"\n   Corrigiendo {count} vales: {tipo_incorrecto} → {tipo_correcto}")
            
            # Hacer la actualización
            cursor.execute("UPDATE vale SET tipo = ? WHERE tipo = ?", (tipo_correcto, tipo_incorrecto))
            correcciones_realizadas += cursor.rowcount
            
            print(f"   ✅ {cursor.rowcount} registros actualizados")
    
    # 3. Confirmar cambios
    conn.commit()
    
    # 4. Mostrar tipos después de la corrección
    print(f"\n3. TIPOS DESPUÉS DE LA CORRECCIÓN:")
    cursor.execute("SELECT DISTINCT tipo FROM vale WHERE tipo IS NOT NULL")
    tipos_finales = cursor.fetchall()
    for tipo in tipos_finales:
        print(f"   ✅ {tipo[0]}")
    
    # 5. Verificar vales de NAVA MEDRANO específicamente
    print(f"\n4. VALES DE NAVA MEDRANO DESPUÉS DE CORRECCIÓN:")
    cursor.execute("""
        SELECT noVale, tipo, proveedor 
        FROM vale 
        WHERE proveedor LIKE '%NAVA%'
        ORDER BY noVale
    """)
    
    vales_nava = cursor.fetchall()
    for vale in vales_nava:
        print(f"   💳 {vale[0]} → {vale[1]} ({vale[2]})")
    
    conn.close()
    print(f"\n✅ PROCESO COMPLETADO - {correcciones_realizadas} correcciones realizadas")

if __name__ == "__main__":
    corregir_tipos_vale_bd()
