#!/usr/bin/env python3
"""
Script para revisar backups y restaurar la BD correcta
"""
import sys
import os
import sqlite3
import shutil
from datetime import datetime

def revisar_backup_y_restaurar():
    print("=== REVISANDO BACKUP Y RESTAURANDO BD CORRECTA ===")
    
    backup_path = "facturas_backup_20250726_142633.db"
    current_path = "facturas.db"
    
    print(f"\n1. REVISANDO BACKUP: {backup_path}")
    if os.path.exists(backup_path):
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Ver estructura de la tabla vale
        cursor.execute("PRAGMA table_info(vale)")
        columnas_backup = cursor.fetchall()
        print("📋 Estructura tabla 'vale' en BACKUP:")
        for col in columnas_backup:
            print(f"  🔧 {col[1]} ({col[2]})")
        
        # Contar vales
        cursor.execute("SELECT COUNT(*) FROM vale")
        count_backup = cursor.fetchone()[0]
        print(f"💳 Vales en backup: {count_backup}")
        
        if count_backup > 0:
            # Mostrar algunos vales
            cursor.execute("SELECT noVale, proveedor, total FROM vale LIMIT 5")
            vales_muestra = cursor.fetchall()
            print("📄 Muestra de vales en backup:")
            for v in vales_muestra:
                print(f"  {v[0]} - {v[1]} - ${v[2]}")
        
        conn.close()
    else:
        print("❌ No se encontró el backup")
        return
    
    print(f"\n2. REVISANDO BD ACTUAL: {current_path}")
    if os.path.exists(current_path):
        conn = sqlite3.connect(current_path)
        cursor = conn.cursor()
        
        # Ver estructura
        cursor.execute("PRAGMA table_info(vale)")
        columnas_current = cursor.fetchall()
        print("📋 Estructura tabla 'vale' en ACTUAL:")
        for col in columnas_current:
            print(f"  🔧 {col[1]} ({col[2]})")
        
        # Contar vales
        cursor.execute("SELECT COUNT(*) FROM vale")
        count_current = cursor.fetchone()[0]
        print(f"💳 Vales en actual: {count_current}")
        
        conn.close()
    
    # Si el backup tiene una mejor estructura o datos, restaurarlo
    print(f"\n3. DECISIÓN DE RESTAURACIÓN:")
    if count_backup > count_current:
        print("✅ El backup tiene más datos, restaurando...")
        
        # Hacer backup del actual
        backup_actual = f"facturas_current_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(current_path, backup_actual)
        print(f"💾 Backup del actual creado: {backup_actual}")
        
        # Restaurar desde backup
        shutil.copy2(backup_path, current_path)
        print(f"✅ BD restaurada desde backup")
        
        # Verificar resultado
        conn = sqlite3.connect(current_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vale")
        count_final = cursor.fetchone()[0]
        print(f"🎯 Vales en BD restaurada: {count_final}")
        
        # Buscar vales de NAVA MEDRANO
        cursor.execute("""
            SELECT noVale, proveedor, total, descripcion 
            FROM vale 
            WHERE proveedor LIKE '%NAVA%' OR proveedor LIKE '%MEDRANO%' 
            LIMIT 5
        """)
        vales_nava = cursor.fetchall()
        
        if vales_nava:
            print(f"\n🏢 VALES DE SERVICIO NAVA MEDRANO ENCONTRADOS:")
            for v in vales_nava:
                print(f"  📄 {v[0]} - {v[1]} - ${v[2]} - {v[3][:50]}...")
        else:
            print(f"\n⚠️ No se encontraron vales de NAVA MEDRANO en la BD restaurada")
        
        conn.close()
    else:
        print("⚠️ La BD actual parece estar bien, no se requiere restauración")

if __name__ == "__main__":
    revisar_backup_y_restaurar()
