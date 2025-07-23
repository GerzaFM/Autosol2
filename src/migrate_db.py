"""
Script de migración para agregar las columnas cargada y pagada a la tabla Factura.
"""
import sys
import os

# Agregar el path de src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bd.models import db, Factura
import sqlite3

def migrate_database():
    """Ejecuta la migración para agregar columnas cargada y pagada."""
    try:
        print("=== Migración de Base de Datos ===")
        
        # Configurar la ruta de la base de datos
        db_path = os.path.join('..', 'facturas.db')
        db_path = os.path.abspath(db_path)
        
        print(f"Migrando BD en: {db_path}")
        
        # Inicializar la conexión
        db.init(db_path)
        db.connect(reuse_if_open=True)
        
        # Verificar si las columnas ya existen
        cursor = db.execute_sql("PRAGMA table_info(factura)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Columnas existentes:", columns)
        
        # Agregar columna cargada si no existe
        if 'cargada' not in columns:
            print("Agregando columna 'cargada'...")
            db.execute_sql("ALTER TABLE factura ADD COLUMN cargada BOOLEAN DEFAULT 0")
            print("✅ Columna 'cargada' agregada")
        else:
            print("✅ Columna 'cargada' ya existe")
        
        # Agregar columna pagada si no existe
        if 'pagada' not in columns:
            print("Agregando columna 'pagada'...")
            db.execute_sql("ALTER TABLE factura ADD COLUMN pagada BOOLEAN DEFAULT 0")
            print("✅ Columna 'pagada' agregada")
        else:
            print("✅ Columna 'pagada' ya existe")
        
        # Verificar las nuevas columnas
        cursor = db.execute_sql("PRAGMA table_info(factura)")
        columns = [row[1] for row in cursor.fetchall()]
        print("Columnas después de la migración:", columns)
        
        # Actualizar algunas facturas de ejemplo con diferentes valores
        print("\n=== Actualizando facturas de ejemplo ===")
        
        # Actualizar la primera factura para que esté cargada pero no pagada
        db.execute_sql("UPDATE factura SET cargada = 1, pagada = 0 WHERE folio_interno = 1")
        print("✅ Factura 1 actualizada: cargada=Sí, pagada=No")
        
        # Verificar la actualización
        cursor = db.execute_sql("SELECT folio_interno, serie, folio, cargada, pagada FROM factura LIMIT 3")
        print("\n=== Facturas actualizadas ===")
        for row in cursor.fetchall():
            folio_interno, serie, folio, cargada, pagada = row
            cargada_str = "Sí" if cargada else "No"
            pagada_str = "Sí" if pagada else "No"
            print(f"ID: {folio_interno}, Serie-Folio: {serie}-{folio}, Cargada: {cargada_str}, Pagada: {pagada_str}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_database()
