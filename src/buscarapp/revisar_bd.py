#!/usr/bin/env python3
"""
Script para revisar la base de datos de vales
"""
import sys
import os
sys.path.insert(0, '..')

import sqlite3

def revisar_bd_vales():
    print("=== REVISANDO BASE DE DATOS DE VALES ===")
    
    # Conectar a la base de datos
    db_paths = [
        '../../facturas.db',
        '../facturas.db',
        '../../src/solicitudapp/facturas.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"✅ Encontrada base de datos en: {path}")
            break
    
    if not db_path:
        print(f"❌ No se encontró ninguna base de datos en las rutas: {db_paths}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Buscar vales de SERVICIO NAVA MEDRANO
        print("\n1. BUSCANDO VALES DE SERVICIO NAVA MEDRANO:")
        cursor.execute("""
            SELECT noVale, proveedor, total, descripcion, fechaVale 
            FROM vale 
            WHERE proveedor LIKE '%NAVA%' OR proveedor LIKE '%MEDRANO%' 
            ORDER BY fechaVale DESC 
            LIMIT 10
        """)
        resultados_nava = cursor.fetchall()
        
        if resultados_nava:
            for r in resultados_nava:
                print(f"  ✅ Vale: {r[0]} | Proveedor: {r[1]} | Total: {r[2]} | Desc: {r[3][:50]}... | Fecha: {r[4]}")
        else:
            print("  ❌ No se encontraron vales de SERVICIO NAVA MEDRANO")
        
        # 2. Contar todos los vales en la BD
        print(f"\n2. TOTAL DE VALES EN LA BASE DE DATOS:")
        cursor.execute("SELECT COUNT(*) FROM vale")
        total_vales = cursor.fetchone()[0]
        print(f"  📊 Total de vales: {total_vales}")
        
        # 3. Últimos 10 vales agregados
        print(f"\n3. ÚLTIMOS 10 VALES AGREGADOS:")
        cursor.execute("""
            SELECT noVale, proveedor, total, fechaVale 
            FROM vale 
            ORDER BY rowid DESC 
            LIMIT 10
        """)
        ultimos_vales = cursor.fetchall()
        
        for r in ultimos_vales:
            print(f"  📄 Vale: {r[0]} | Proveedor: {r[1]} | Total: {r[2]} | Fecha: {r[3]}")
        
        # 4. Verificar estructura de la tabla
        print(f"\n4. ESTRUCTURA DE LA TABLA VALE:")
        cursor.execute("PRAGMA table_info(vale)")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  🔧 {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    revisar_bd_vales()
