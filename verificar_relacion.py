#!/usr/bin/env python3
"""
Script para verificar relación facturas-vales
"""
import sqlite3

def verificar_relacion_facturas_vales():
    print("=== VERIFICANDO RELACIÓN FACTURAS-VALES ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # 1. Buscar facturas y vales de NAVA MEDRANO
    print("\n1. FACTURAS CON VALES DE NAVA MEDRANO:")
    cursor.execute("""
        SELECT f.folio_interno, f.nombre_emisor, v.noVale, v.tipo, v.proveedor, v.factura_id
        FROM factura f 
        LEFT JOIN vale v ON f.folio_interno = v.factura_id 
        WHERE f.nombre_emisor LIKE '%NAVA%' OR v.proveedor LIKE '%NAVA%'
        ORDER BY f.folio_interno
    """)
    
    resultados = cursor.fetchall()
    print(f"Facturas con vales de NAVA MEDRANO: {len(resultados)}")
    for r in resultados:
        print(f"  📄 Factura: {r[0]} | Emisor: {r[1]} | Vale: {r[2]} | Tipo: {r[3]} | Proveedor Vale: {r[4]} | Relación: {r[5]}")
    
    # 2. Buscar vales sin factura asociada
    print(f"\n2. VALES SIN FACTURA ASOCIADA:")
    cursor.execute("""
        SELECT noVale, tipo, proveedor, factura_id 
        FROM vale 
        WHERE (proveedor LIKE '%NAVA%' OR proveedor LIKE '%MEDRANO%') 
        AND (factura_id IS NULL OR factura_id = 0)
    """)
    
    vales_sin_factura = cursor.fetchall()
    print(f"Vales sin factura: {len(vales_sin_factura)}")
    for v in vales_sin_factura:
        print(f"  💳 Vale: {v[0]} | Tipo: {v[1]} | Proveedor: {v[2]} | Factura ID: {v[3]}")
    
    # 3. Verificar qué contiene el campo 'tipo' del vale
    print(f"\n3. TIPOS DE VALE EN LA BD (campo 'tipo'):")
    cursor.execute("SELECT DISTINCT tipo FROM vale WHERE tipo IS NOT NULL AND tipo != ''")
    tipos = cursor.fetchall()
    print(f"Tipos encontrados: {len(tipos)}")
    for t in tipos:
        print(f"  🏷️ '{t[0]}'")
    
    # 4. Ver estructura de tabla vale
    print(f"\n4. ESTRUCTURA TABLA VALE:")
    cursor.execute("PRAGMA table_info(vale)")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"  🔧 {col[1]} ({col[2]})")
    
    # 5. Ejemplo de vale completo
    print(f"\n5. EJEMPLO DE VALE COMPLETO:")
    cursor.execute("SELECT * FROM vale WHERE proveedor LIKE '%NAVA%' LIMIT 1")
    vale_ejemplo = cursor.fetchone()
    if vale_ejemplo:
        cursor.execute("PRAGMA table_info(vale)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        for i, valor in enumerate(vale_ejemplo):
            print(f"  {columnas[i]}: {valor}")
    
    conn.close()

if __name__ == "__main__":
    verificar_relacion_facturas_vales()
