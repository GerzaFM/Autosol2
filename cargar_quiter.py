#!/usr/bin/env python3
"""
Script para cargar datos de proveedores desde BD.txt y poblar el campo nombre_en_quiter
"""
import sys
import os
from pathlib import Path

# Agregar path para acceder a los modelos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from bd.models import Proveedor, db
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    sys.exit(1)

def cargar_proveedores_quiter():
    """Cargar proveedores desde BD.txt y actualizar nombre_en_quiter"""
    
    bd_file = "BD.txt"
    
    if not os.path.exists(bd_file):
        print(f"❌ Error: No se encuentra el archivo {bd_file}")
        return False
    
    try:
        # Conectar a la base de datos
        db.connect()
        
        # Leer archivo BD.txt
        with open(bd_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        proveedores_actualizados = 0
        proveedores_creados = 0
        errores = 0
        
        print(f"📖 Leyendo {len(lines)} líneas de {bd_file}")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parsear línea: código\tnombre
                parts = line.split('\t')
                if len(parts) != 2:
                    print(f"⚠️  Línea {line_num}: formato inválido - {line}")
                    errores += 1
                    continue
                
                codigo_str, nombre_quiter = parts
                codigo_quiter = int(codigo_str)
                
                # Buscar si ya existe un proveedor con este código
                proveedor_existente = Proveedor.select().where(
                    Proveedor.codigo_quiter == codigo_quiter
                ).first()
                
                if proveedor_existente:
                    # Actualizar el campo nombre_en_quiter
                    proveedor_existente.nombre_en_quiter = nombre_quiter
                    proveedor_existente.save()
                    proveedores_actualizados += 1
                    print(f"✅ Actualizado proveedor ID {proveedor_existente.id}: {nombre_quiter}")
                else:
                    # Crear nuevo proveedor con datos mínimos
                    # Usar nombre_quiter como nombre base y generar un RFC temporal
                    rfc_temporal = f"QUITER{codigo_quiter:06d}XXX"
                    
                    nuevo_proveedor = Proveedor.create(
                        nombre=nombre_quiter,
                        rfc=rfc_temporal,
                        codigo_quiter=codigo_quiter,
                        nombre_en_quiter=nombre_quiter
                    )
                    proveedores_creados += 1
                    print(f"🆕 Creado proveedor ID {nuevo_proveedor.id}: {nombre_quiter}")
                
            except ValueError as e:
                print(f"⚠️  Línea {line_num}: error de conversión - {line} - {e}")
                errores += 1
                continue
            except Exception as e:
                print(f"❌ Línea {line_num}: error inesperado - {e}")
                errores += 1
                continue
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Proveedores actualizados: {proveedores_actualizados}")
        print(f"   🆕 Proveedores creados: {proveedores_creados}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📋 Total procesado: {proveedores_actualizados + proveedores_creados}")
        
        return errores == 0
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    print("=== CARGAR DATOS DE QUITER ===")
    
    success = cargar_proveedores_quiter()
    
    if success:
        print("\n🎉 Carga de datos completada exitosamente")
        print("📌 El campo nombre_en_quiter está listo para usar en cheques")
    else:
        print("\n💥 La carga de datos tuvo errores")
        sys.exit(1)
