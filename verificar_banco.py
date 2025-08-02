#!/usr/bin/env python3
"""
Script para verificar y actualizar la tabla banco con el campo cuenta_mayor
"""
import sqlite3
import os

def verificar_y_actualizar_banco():
    # Configurar la ruta absoluta a la base de datos
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, 'facturas.db')
    
    print(f"Conectando a la base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== VERIFICANDO ESTRUCTURA DE LA TABLA BANCO ===")
        cursor.execute("PRAGMA table_info(banco)")
        columns = cursor.fetchall()
        
        print("Estructura actual de la tabla banco:")
        for col in columns:
            null_info = "NULL permitido" if col[3] == 0 else "NOT NULL"
            print(f"  - {col[1]}: {col[2]} ({null_info})")
        
        # Verificar si cuenta_mayor existe
        cuenta_mayor_exists = any(col[1] == 'cuenta_mayor' for col in columns)
        
        if not cuenta_mayor_exists:
            print("\n❌ El campo cuenta_mayor NO existe en la tabla banco")
            print("Agregando el campo cuenta_mayor...")
            
            cursor.execute("ALTER TABLE banco ADD COLUMN cuenta_mayor INTEGER")
            conn.commit()
            print("✅ Campo cuenta_mayor agregado exitosamente")
            
            # Verificar que se agregó correctamente
            cursor.execute("PRAGMA table_info(banco)")
            columns = cursor.fetchall()
            print("\nEstructura actualizada:")
            for col in columns:
                null_info = "NULL permitido" if col[3] == 0 else "NOT NULL"
                print(f"  - {col[1]}: {col[2]} ({null_info})")
        else:
            print("\n✅ El campo cuenta_mayor ya existe en la tabla banco")
        
        # Mostrar datos existentes
        print("\n=== DATOS EN LA TABLA BANCO ===")
        cursor.execute("SELECT COUNT(*) FROM banco")
        count = cursor.fetchone()[0]
        print(f"Total de registros en banco: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, nombre, cuenta, codigo, cuenta_mayor FROM banco LIMIT 5")
            bancos = cursor.fetchall()
            
            print("Primeros 5 registros:")
            for banco in bancos:
                print(f"  ID: {banco[0]}, Nombre: {banco[1]}, Cuenta: {banco[2]}, Código: {banco[3]}, Cuenta Mayor: {banco[4]}")
        else:
            print("No hay registros en la tabla banco")
        
        conn.close()
        print("\n✅ Proceso completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verificar_y_actualizar_banco()
