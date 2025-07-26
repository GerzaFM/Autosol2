#!/usr/bin/env python3
"""
Script para asociar vales con facturas
"""
import sqlite3

def asociar_vales_con_facturas():
    print("=== ASOCIANDO VALES CON FACTURAS ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Ver qué facturas de NAVA MEDRANO tenemos
    print("\n1. FACTURAS DE NAVA MEDRANO DISPONIBLES:")
    cursor.execute("""
        SELECT folio_interno, nombre_emisor, fecha_factura, total 
        FROM factura 
        WHERE nombre_emisor LIKE '%NAVA%'
        ORDER BY folio_interno
    """)
    
    facturas = cursor.fetchall()
    for f in facturas:
        print(f"  📄 Folio: {f[0]} | Emisor: {f[1]} | Fecha: {f[2]} | Total: {f[3]}")
    
    # 2. Ver vales sin asociar
    print(f"\n2. VALES SIN ASOCIAR:")
    cursor.execute("""
        SELECT id, noVale, tipo, total, fechaVale, proveedor 
        FROM vale 
        WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
        ORDER BY fechaVale
    """)
    
    vales = cursor.fetchall()
    for v in vales:
        print(f"  💳 ID: {v[0]} | Vale: {v[1]} | Tipo: {v[2]} | Total: {v[3]} | Fecha: {v[4]} | Proveedor: {v[5]}")
    
    # 3. Estrategia de asociación (ejemplo)
    print(f"\n3. SUGERENCIA DE ASOCIACIÓN:")
    if len(facturas) > 0 and len(vales) > 0:
        print("Podemos asociar los vales con las facturas de varias maneras:")
        print("  A) Por fecha más cercana")
        print("  B) Por total similar")
        print("  C) Asociar todos los vales con la primera factura")
        print("  D) Distribución equitativa")
        
        # Ejemplo: asociar todos con la primera factura para prueba
        primera_factura = facturas[0][0]  # folio_interno
        print(f"\n   Ejemplo: Asociar todos los vales con factura {primera_factura}")
        
        respuesta = input("¿Quieres asociar todos los vales de NAVA MEDRANO con la factura más reciente? (s/n): ")
        
        if respuesta.lower() == 's':
            # Usar la factura más reciente (mayor folio)
            factura_destino = max(facturas, key=lambda x: x[0])[0]
            print(f"\nAsociando todos los vales con factura {factura_destino}...")
            
            cursor.execute("""
                UPDATE vale 
                SET factura_id = ? 
                WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
            """, (factura_destino,))
            
            conn.commit()
            print(f"✅ Asociados {cursor.rowcount} vales con factura {factura_destino}")
            
            # Verificar resultado
            cursor.execute("""
                SELECT f.folio_interno, f.nombre_emisor, v.noVale, v.tipo 
                FROM factura f 
                JOIN vale v ON f.folio_interno = v.factura_id 
                WHERE f.folio_interno = ?
            """, (factura_destino,))
            
            resultado = cursor.fetchall()
            print(f"\nVERIFICACIÓN - Factura {factura_destino} ahora tiene {len(resultado)} vales:")
            for r in resultado:
                print(f"  ✅ {r[2]} ({r[3]})")
    
    conn.close()

if __name__ == "__main__":
    asociar_vales_con_facturas()
