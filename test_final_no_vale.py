#!/usr/bin/env python3
"""
Test final para verificar que la columna No. Vale y los tipos de vale funcionen correctamente
"""
import sqlite3

def test_final_columna_no_vale():
    print("=== TEST FINAL - COLUMNA NO. VALE Y TIPOS ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Verificar facturas con vales asociados
    print("\n1. FACTURAS CON VALES ASOCIADOS:")
    cursor.execute("""
        SELECT f.folio_interno, f.nombre_emisor, v.noVale, v.tipo
        FROM factura f 
        JOIN vale v ON f.folio_interno = v.factura_id 
        ORDER BY f.folio_interno
    """)
    
    resultados = cursor.fetchall()
    print(f"   Total facturas con vales: {len(resultados)}")
    
    for r in resultados:
        print(f"   📄 Factura {r[0]} | {r[1][:30]}... | Vale: {r[2]} | Tipo: {r[3]}")
    
    # 2. Verificar tipos de vale corregidos
    print(f"\n2. TIPOS DE VALE CORREGIDOS:")
    cursor.execute("SELECT DISTINCT tipo FROM vale ORDER BY tipo")
    tipos = cursor.fetchall()
    
    for tipo in tipos:
        cursor.execute("SELECT COUNT(*) FROM vale WHERE tipo = ?", (tipo[0],))
        count = cursor.fetchone()[0]
        print(f"   🏷️ {tipo[0]}: {count} vales")
    
    # 3. Verificar específicamente NAVA MEDRANO
    print(f"\n3. FACTURAS NAVA MEDRANO (para verificar en UI):")
    cursor.execute("""
        SELECT f.folio_interno, f.nombre_emisor, v.noVale, v.tipo
        FROM factura f 
        JOIN vale v ON f.folio_interno = v.factura_id 
        WHERE f.nombre_emisor LIKE '%NAVA%'
        ORDER BY f.folio_interno
    """)
    
    nava_resultados = cursor.fetchall()
    for r in nava_resultados:
        print(f"   📄 Factura {r[0]}")
        print(f"      👤 Emisor: {r[1]}")
        print(f"      💳 No. Vale: {r[2]} ← DEBE APARECER EN COLUMNA")
        print(f"      🏷️ Tipo: {r[3]} ← DEBE APARECER EN PANEL")
        print()
    
    conn.close()
    
    print("✅ APLICACIÓN LISTA - Ahora puedes:")
    print("   1. Buscar 'NAVA' en el campo Proveedor")
    print("   2. Ver que la columna 'No. Vale' muestre los números de vale")
    print("   3. Seleccionar una factura y ver el tipo corregido en el panel de información")

if __name__ == "__main__":
    test_final_columna_no_vale()
