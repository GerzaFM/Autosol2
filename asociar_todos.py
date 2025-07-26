#!/usr/bin/env python3
"""
Script para asociar todos los vales restantes
"""
import sqlite3

def asociar_todos_los_vales():
    print("=== ASOCIANDO TODOS LOS VALES RESTANTES ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Ver vales sin asociar
    cursor.execute("""
        SELECT id, noVale, tipo 
        FROM vale 
        WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
    """)
    vales_sin_asociar = cursor.fetchall()
    
    # 2. Ver facturas disponibles sin vales
    cursor.execute("""
        SELECT f.folio_interno 
        FROM factura f 
        LEFT JOIN vale v ON f.folio_interno = v.factura_id 
        WHERE f.nombre_emisor LIKE '%NAVA%' AND v.factura_id IS NULL
    """)
    facturas_libres = cursor.fetchall()
    
    print(f"Vales sin asociar: {len(vales_sin_asociar)}")
    print(f"Facturas libres: {len(facturas_libres)}")
    
    # 3. Asociar vales con facturas disponibles
    asociaciones = 0
    for i, vale in enumerate(vales_sin_asociar):
        if i < len(facturas_libres):
            vale_id = vale[0]
            vale_numero = vale[1]
            factura_id = facturas_libres[i][0]
            
            try:
                cursor.execute("UPDATE vale SET factura_id = ? WHERE id = ?", (factura_id, vale_id))
                conn.commit()
                print(f"✅ Vale {vale_numero} → Factura {factura_id}")
                asociaciones += 1
            except sqlite3.IntegrityError as e:
                print(f"❌ Error con vale {vale_numero}: {e}")
    
    # 4. Para vales restantes, usar facturas que ya tienen vales (relación múltiple)
    if asociaciones < len(vales_sin_asociar):
        print(f"\nQuedan {len(vales_sin_asociar) - asociaciones} vales sin asociar")
        
        # Obtener todas las facturas NAVA
        cursor.execute("SELECT folio_interno FROM factura WHERE nombre_emisor LIKE '%NAVA%'")
        todas_facturas = cursor.fetchall()
        
        # Obtener vales restantes
        cursor.execute("""
            SELECT id, noVale 
            FROM vale 
            WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
        """)
        vales_restantes = cursor.fetchall()
        
        for i, vale in enumerate(vales_restantes):
            vale_id = vale[0]
            vale_numero = vale[1]
            # Rotar entre las facturas disponibles
            factura_id = todas_facturas[i % len(todas_facturas)][0]
            
            try:
                cursor.execute("UPDATE vale SET factura_id = ? WHERE id = ?", (factura_id, vale_id))
                conn.commit()
                print(f"✅ Vale {vale_numero} → Factura {factura_id} (múltiple)")
                asociaciones += 1
            except sqlite3.IntegrityError as e:
                print(f"❌ Error con vale {vale_numero}: {e}")
    
    # 5. Verificar resultado final
    print(f"\n=== RESULTADO FINAL ===")
    cursor.execute("""
        SELECT f.folio_interno, f.serie, f.folio, COUNT(v.id) as total_vales
        FROM factura f 
        LEFT JOIN vale v ON f.folio_interno = v.factura_id 
        WHERE f.nombre_emisor LIKE '%NAVA%'
        GROUP BY f.folio_interno
        ORDER BY f.folio_interno
    """)
    
    resultado = cursor.fetchall()
    for r in resultado:
        print(f"📄 Factura {r[0]} ({r[1]}{r[2]}) tiene {r[3]} vales")
    
    conn.close()
    print(f"\n✅ Total asociaciones realizadas: {asociaciones}")

if __name__ == "__main__":
    asociar_todos_los_vales()
