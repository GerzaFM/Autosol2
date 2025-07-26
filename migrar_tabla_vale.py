#!/usr/bin/env python3
"""
Script de migración para actualizar el modelo Vale en la base de datos.
Cambios:
1. Agregar campo 'id' como nueva clave primaria autoincremental
2. Cambiar 'noVale' de primary key a unique
3. Agregar campo 'cuenta' 
4. Corregir typo: 'departameto' -> 'departamento'
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bd.models import db, Vale
from peewee import *

def migrar_tabla_vale():
    """
    Migra la tabla Vale a la nueva estructura.
    """
    print("🔄 INICIANDO MIGRACIÓN DE TABLA VALE")
    print("=" * 50)
    
    try:
        # Conectar a la base de datos
        db.connect()
        
        # Verificar si la tabla existe
        if not Vale.table_exists():
            print("📋 Tabla Vale no existe. Creando nueva tabla...")
            Vale.create_table()
            print("✅ Tabla Vale creada exitosamente.")
            return
        
        print("📋 Tabla Vale existe. Verificando estructura...")
        
        # Obtener información de columnas actuales
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        columnas_actuales = {row[1]: row for row in cursor.fetchall()}
        
        print(f"📊 Columnas actuales encontradas: {list(columnas_actuales.keys())}")
        
        # Verificar si ya tiene la nueva estructura
        if 'id' in columnas_actuales and 'cuenta' in columnas_actuales and 'departamento' in columnas_actuales:
            print("✅ La tabla ya tiene la estructura actualizada.")
            return
        
        # Realizar migración
        print("🔧 Realizando migración...")
        
        # 1. Crear tabla temporal con nueva estructura
        db.execute_sql("""
            CREATE TABLE vale_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                noVale VARCHAR(255) UNIQUE NOT NULL,
                tipo VARCHAR(255) NOT NULL,
                noDocumento VARCHAR(255) NOT NULL,
                descripcion VARCHAR(255) NOT NULL,
                referencia INTEGER NOT NULL,
                total VARCHAR(255) NOT NULL,
                cuenta INTEGER,
                fechaVale DATE,
                departamento INTEGER,
                sucursal INTEGER,
                marca INTEGER,
                responsable INTEGER,
                proveedor VARCHAR(255),
                factura_id INTEGER,
                FOREIGN KEY (factura_id) REFERENCES factura (folio_interno)
            )
        """)
        print("✅ Tabla temporal creada.")
        
        # 2. Copiar datos existentes (si los hay)
        cursor = db.execute_sql("SELECT COUNT(*) FROM vale")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"📦 Copiando {count} registros existentes...")
            
            # Mapear columnas antiguas a nuevas
            if 'departameto' in columnas_actuales:  # Tiene el typo
                db.execute_sql("""
                    INSERT INTO vale_new (noVale, tipo, noDocumento, descripcion, referencia, total, 
                                         fechaVale, departamento, sucursal, marca, responsable, proveedor, factura_id)
                    SELECT noVale, tipo, noDocumento, descripcion, referencia, total, 
                           fechaVale, departameto, sucursal, marca, responsable, proveedor, factura_id
                    FROM vale
                """)
            else:
                db.execute_sql("""
                    INSERT INTO vale_new (noVale, tipo, noDocumento, descripcion, referencia, total, 
                                         fechaVale, departamento, sucursal, marca, responsable, proveedor, factura_id)
                    SELECT noVale, tipo, noDocumento, descripcion, referencia, total, 
                           fechaVale, departamento, sucursal, marca, responsable, proveedor, factura_id
                    FROM vale
                """)
            print("✅ Datos copiados exitosamente.")
        
        # 3. Eliminar tabla antigua y renombrar la nueva
        db.execute_sql("DROP TABLE vale")
        db.execute_sql("ALTER TABLE vale_new RENAME TO vale")
        print("✅ Tabla migrada exitosamente.")
        
        # 4. Verificar nueva estructura
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        nuevas_columnas = [row[1] for row in cursor.fetchall()]
        print(f"📊 Nueva estructura: {nuevas_columnas}")
        
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        # Intentar rollback si es posible
        try:
            db.execute_sql("DROP TABLE IF EXISTS vale_new")
        except:
            pass
        raise
    
    finally:
        if not db.is_closed():
            db.close()

def verificar_migracion():
    """
    Verifica que la migración se haya realizado correctamente.
    """
    print("\n🔍 VERIFICANDO MIGRACIÓN")
    print("=" * 30)
    
    try:
        db.connect()
        
        # Verificar estructura de tabla
        cursor = db.execute_sql("PRAGMA table_info(vale)")
        columnas = {row[1]: {'tipo': row[2], 'pk': row[5]} for row in cursor.fetchall()}
        
        campos_esperados = {
            'id': {'tipo': 'INTEGER', 'pk': 1},
            'noVale': {'tipo': 'VARCHAR(255)', 'pk': 0},
            'cuenta': {'tipo': 'INTEGER', 'pk': 0},
            'departamento': {'tipo': 'INTEGER', 'pk': 0}
        }
        
        print("📋 Verificando campos críticos:")
        for campo, props in campos_esperados.items():
            if campo in columnas:
                if columnas[campo]['pk'] == props['pk']:
                    print(f"✅ {campo}: OK ({columnas[campo]['tipo']})")
                else:
                    print(f"⚠️  {campo}: PK incorrecta")
            else:
                print(f"❌ {campo}: NO ENCONTRADO")
        
        # Verificar que no existe el campo con typo
        if 'departameto' not in columnas:
            print("✅ Typo 'departameto' corregido")
        else:
            print("⚠️  Aún existe 'departameto'")
        
        print("✅ Verificación completada.")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    migrar_tabla_vale()
    verificar_migracion()
