#!/usr/bin/env python3
"""
Script para verificar constrains y asociar vales individualmente
"""
import sqlite3

def asociar_vales_individual():
    print("=== ASOCIANDO VALES INDIVIDUALMENTE ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Ver schema de la tabla vale
    print("\n1. SCHEMA DE TABLA VALE:")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='vale'")
    schema = cursor.fetchone()
    if schema:
        print(f"   {schema[0]}")
    
    # 2. Ver vales sin asociar
    print(f"\n2. VALES SIN ASOCIAR:")
    cursor.execute("""
        SELECT id, noVale, tipo, proveedor 
        FROM vale 
        WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
        LIMIT 3
    """)
    
    vales = cursor.fetchall()
    for v in vales:
        print(f"   💳 ID: {v[0]} | Vale: {v[1]} | Tipo: {v[2]} | Proveedor: {v[3]}")
    
    # 3. Ver facturas disponibles
    print(f"\n3. FACTURAS NAVA MEDRANO:")
    cursor.execute("SELECT folio_interno, serie, folio FROM factura WHERE nombre_emisor LIKE '%NAVA%'")
    facturas = cursor.fetchall()
    for f in facturas:
        print(f"   📄 Folio interno: {f[0]} | Serie: {f[1]} | Folio: {f[2]}")
    
    # 4. Intentar asociar uno por uno
    print(f"\n4. ASOCIANDO VALE POR VALE:")
    
    # Primero verificar si alguna factura ya tiene vales
    for factura in facturas:
        folio = factura[0]
        cursor.execute("SELECT COUNT(*) FROM vale WHERE factura_id = ?", (folio,))
        count = cursor.fetchone()[0]
        print(f"   Factura {folio} tiene {count} vales asociados")
    
    # Asociar primer vale con primera factura disponible
    if vales and facturas:
        vale_id = vales[0][0]
        factura_destino = facturas[0][0]  # Usar primera factura
        
        try:
            print(f"\n   Intentando asociar vale ID {vale_id} con factura {factura_destino}...")
            cursor.execute("UPDATE vale SET factura_id = ? WHERE id = ?", (factura_destino, vale_id))
            conn.commit()
            print(f"   ✅ Éxito: Vale {vale_id} asociado con factura {factura_destino}")
            
            # Verificar
            cursor.execute("SELECT noVale, tipo FROM vale WHERE id = ?", (vale_id,))
            vale_info = cursor.fetchone()
            print(f"   📊 Vale actualizado: {vale_info[0]} ({vale_info[1]})")
            
        except sqlite3.IntegrityError as e:
            print(f"   ❌ Error: {e}")
            print("   Posiblemente cada factura solo puede tener un vale")
            
            # Intentar con otra factura
            for i, factura in enumerate(facturas[1:], 1):
                try:
                    factura_alt = factura[0]
                    print(f"   Intentando con factura alternativa {factura_alt}...")
                    cursor.execute("UPDATE vale SET factura_id = ? WHERE id = ?", (factura_alt, vale_id))
                    conn.commit()
                    print(f"   ✅ Éxito con factura alternativa {factura_alt}")
                    break
                except sqlite3.IntegrityError:
                    print(f"   ❌ Factura {factura_alt} también falló")
                    continue
    
    conn.close()
    print("\n✅ PROCESO COMPLETADO")

if __name__ == "__main__":
    asociar_vales_individual()
