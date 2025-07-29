#!/usr/bin/env python3
"""
Script para agregar el campo 'codigo' a la tabla Vale en la base de datos.
"""

import sqlite3
import os
from pathlib import Path

def agregar_campo_codigo():
    """Agrega el campo codigo a la tabla Vale."""
    
    # Ruta de la base de datos
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    db_path = project_root / "facturas.db"
    
    print(f"Conectando a la base de datos: {db_path}")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(vale)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'codigo' in columns:
            print("❌ La columna 'codigo' ya existe en la tabla Vale")
            return False
        
        # Agregar la columna codigo
        print("🔄 Agregando columna 'codigo' a la tabla Vale...")
        cursor.execute("ALTER TABLE vale ADD COLUMN codigo VARCHAR(255) NULL")
        
        conn.commit()
        print("✅ Columna 'codigo' agregada exitosamente")
        
        # Verificar que se agregó correctamente
        cursor.execute("PRAGMA table_info(vale)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Columnas actuales en la tabla Vale: {', '.join(columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al agregar la columna: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("🔒 Conexión cerrada")

if __name__ == "__main__":
    print("=== MIGRACIÓN: Agregar campo 'codigo' a tabla Vale ===")
    success = agregar_campo_codigo()
    
    if success:
        print("\n✅ Migración completada exitosamente")
        print("💡 Ahora puedes actualizar el código para usar el nuevo campo")
    else:
        print("\n❌ La migración falló o ya se había ejecutado")
