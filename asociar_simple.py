#!/usr/bin/env python3
"""
Script simple para ver estructura de facturas y asociar vales
"""
import sqlite3

def asociar_vales_simple():
    print("=== ASOCIANDO VALES CON FACTURAS (SIMPLE) ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Ver estructura de factura
    print("\n1. ESTRUCTURA TABLA FACTURA:")
    cursor.execute("PRAGMA table_info(factura)")
    columnas_factura = cursor.fetchall()
    for col in columnas_factura:
        print(f"  🔧 {col[1]} ({col[2]})")
    
    # 2. Ver facturas NAVA MEDRANO
    print(f"\n2. FACTURAS DE NAVA MEDRANO:")
    cursor.execute("SELECT * FROM factura WHERE nombre_emisor LIKE '%NAVA%' LIMIT 3")
    facturas = cursor.fetchall()
    
    # Obtener nombres de columnas
    cursor.execute("PRAGMA table_info(factura)")
    nombres_cols = [col[1] for col in cursor.fetchall()]
    
    for i, factura in enumerate(facturas):
        print(f"\n  📄 FACTURA {i+1}:")
        for j, valor in enumerate(factura):
            if j < len(nombres_cols):
                print(f"     {nombres_cols[j]}: {valor}")
    
    # 3. Asociar todos los vales NAVA con la factura más reciente
    print(f"\n3. ASOCIANDO VALES...")
    
    # Buscar factura más reciente
    cursor.execute("SELECT folio_interno FROM factura WHERE nombre_emisor LIKE '%NAVA%' ORDER BY folio_interno DESC LIMIT 1")
    factura_reciente = cursor.fetchone()
    
    if factura_reciente:
        folio_destino = factura_reciente[0]
        print(f"   Factura destino: {folio_destino}")
        
        # Actualizar vales
        cursor.execute("""
            UPDATE vale 
            SET factura_id = ? 
            WHERE proveedor LIKE '%NAVA%' AND factura_id IS NULL
        """, (folio_destino,))
        
        conn.commit()
        print(f"   ✅ Asociados {cursor.rowcount} vales con factura {folio_destino}")
        
        # Verificar
        cursor.execute("""
            SELECT COUNT(*) 
            FROM vale 
            WHERE factura_id = ?
        """, (folio_destino,))
        
        total_vales = cursor.fetchone()[0]
        print(f"   📊 Total vales en factura {folio_destino}: {total_vales}")
    
    conn.close()
    print("\n✅ PROCESO COMPLETADO")

if __name__ == "__main__":
    asociar_vales_simple()
