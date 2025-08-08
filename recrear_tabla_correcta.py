#!/usr/bin/env python3
"""
Script para recrear la tabla proveedor con el nuevo esquema
"""
import sys
import os
import sqlite3

def recrear_tabla_proveedor():
    """Recrear la tabla proveedor con el esquema correcto"""
    
    # Ruta a la base de datos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "facturas.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️ Eliminando tabla proveedor antigua...")
        cursor.execute("DROP TABLE IF EXISTS proveedor")
        
        print("🆕 Creando tabla proveedor nueva con esquema correcto...")
        cursor.execute("""
            CREATE TABLE proveedor (
                id INTEGER PRIMARY KEY,
                nombre TEXT NULL,
                rfc TEXT NULL,
                telefono TEXT NULL,
                email TEXT NULL,
                nombre_contacto TEXT NULL,
                codigo_quiter INTEGER NULL,
                cuenta_mayor INTEGER NULL,
                nombre_en_quiter TEXT NULL
            )
        """)
        
        conn.commit()
        print("✅ Tabla proveedor recreada con éxito")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def cargar_bd_txt():
    """Cargar BD.txt en la nueva tabla"""
    
    bd_file = "BD.txt"
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facturas.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(bd_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        proveedores_creados = 0
        errores = 0
        
        print(f"📖 Cargando {len(lines)} líneas de BD.txt")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split('\t')
                if len(parts) != 2:
                    errores += 1
                    continue
                
                codigo_str, nombre_quiter = parts
                
                try:
                    codigo_quiter = int(codigo_str)
                except ValueError:
                    errores += 1
                    continue
                
                # Insertar SOLO nombre_en_quiter y codigo_quiter
                cursor.execute("""
                    INSERT INTO proveedor (nombre_en_quiter, codigo_quiter)
                    VALUES (?, ?)
                """, (nombre_quiter, codigo_quiter))
                
                proveedores_creados += 1
                if proveedores_creados <= 5:
                    print(f"✅ {codigo_quiter}: '{nombre_quiter}'")
                
            except Exception as e:
                print(f"❌ Error línea {line_num}: {e}")
                errores += 1
        
        conn.commit()
        
        print(f"\n📊 RESULTADO:")
        print(f"   ✅ Creados: {proveedores_creados}")
        print(f"   ❌ Errores: {errores}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verificar_resultado():
    """Verificar el resultado final"""
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facturas.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM proveedor")
        total = cursor.fetchone()[0]
        
        print(f"\n🔍 VERIFICACIÓN:")
        print(f"   Total proveedores: {total}")
        
        cursor.execute("SELECT id, nombre_en_quiter, codigo_quiter, nombre, rfc FROM proveedor LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"\n📋 MUESTRA:")
        for row in rows:
            id_prov, nombre_quiter, codigo_quiter, nombre, rfc = row
            print(f"   ID {id_prov}:")
            print(f"      nombre_en_quiter: '{nombre_quiter}'")
            print(f"      codigo_quiter: {codigo_quiter}")
            print(f"      nombre: {nombre if nombre else 'NULL'}")
            print(f"      rfc: {rfc if rfc else 'NULL'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== RECREAR TABLA Y CARGAR CORRECTAMENTE ===")
    
    # Paso 1: Recrear tabla
    print("\n🔨 PASO 1: Recreando tabla proveedor...")
    if not recrear_tabla_proveedor():
        sys.exit(1)
    
    # Paso 2: Cargar datos
    print("\n📥 PASO 2: Cargando SOLO nombre_en_quiter y codigo_quiter...")
    if not cargar_bd_txt():
        sys.exit(1)
    
    # Paso 3: Verificar
    print("\n🔍 PASO 3: Verificando resultado...")
    verificar_resultado()
    
    print("\n🎉 ¡COMPLETADO CORRECTAMENTE!")
    print("✅ Tabla recreada con esquema correcto")
    print("✅ Cargados SOLO los datos solicitados")
    print("✅ Sin RFC inventados, sin nombres duplicados")
