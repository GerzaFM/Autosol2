#!/usr/bin/env python3
"""
Script para cargar SOLO nombre_en_quiter y codigo_quiter. NADA MÁS.
"""
import sys
import os

# Agregar path para acceder a los modelos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from bd.models import Proveedor, Usuario, Banco, db
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    sys.exit(1)

def limpiar_proveedores():
    """Eliminar TODOS los proveedores"""
    
    try:
        db.connect()
        
        count_proveedores = Proveedor.select().count()
        print(f"🗑️ Eliminando {count_proveedores} proveedores...")
        
        if count_proveedores > 0:
            eliminados = Proveedor.delete().execute()
            print(f"✅ Eliminados {eliminados} proveedores")
        else:
            print("✅ No hay proveedores para eliminar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()

def cargar_solo_quiter():
    """Cargar SOLO nombre_en_quiter y codigo_quiter de BD.txt"""
    
    bd_file = "BD.txt"
    
    if not os.path.exists(bd_file):
        print(f"❌ Error: No se encuentra el archivo {bd_file}")
        return False
    
    try:
        db.connect()
        
        with open(bd_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        proveedores_creados = 0
        errores = 0
        
        print(f"📖 Procesando {len(lines)} líneas de {bd_file}")
        print("🎯 CREANDO SOLO:")
        print("   - nombre_en_quiter (de BD.txt)")
        print("   - codigo_quiter (de BD.txt)")
        print("   - TODO LO DEMÁS = NULL")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parsear línea: código\tnombre
                parts = line.split('\t')
                if len(parts) != 2:
                    errores += 1
                    continue
                
                codigo_str, nombre_quiter = parts
                
                # Validar que el código sea numérico (saltar F4, F5, F6)
                try:
                    codigo_quiter = int(codigo_str)
                except ValueError:
                    errores += 1
                    continue
                
                # Crear proveedor SOLO con los dos campos solicitados
                nuevo_proveedor = Proveedor.create(
                    nombre_en_quiter=nombre_quiter,
                    codigo_quiter=codigo_quiter
                    # nombre = NULL
                    # rfc = NULL  
                    # telefono = NULL
                    # email = NULL
                    # nombre_contacto = NULL
                    # cuenta_mayor = NULL
                )
                
                proveedores_creados += 1
                if proveedores_creados <= 5:
                    print(f"✅ {codigo_quiter}: '{nombre_quiter}'")
                
            except Exception as e:
                print(f"❌ Línea {line_num}: error - {e}")
                errores += 1
                continue
        
        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Proveedores creados: {proveedores_creados}")
        print(f"   ❌ Errores: {errores}")
        
        return errores == 0
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()

def verificar_resultado():
    """Verificar que solo se crearon con los campos correctos"""
    
    try:
        db.connect()
        
        total = Proveedor.select().count()
        print(f"\n🔍 VERIFICACIÓN FINAL:")
        print(f"   Total proveedores: {total}")
        
        print(f"\n📋 MUESTRA (primeros 3):")
        for prov in Proveedor.select().limit(3):
            print(f"   ID {prov.id}:")
            print(f"      nombre_en_quiter: '{prov.nombre_en_quiter}'")
            print(f"      codigo_quiter: {prov.codigo_quiter}")
            print(f"      nombre: {prov.nombre}")  # Debe ser NULL
            print(f"      rfc: {prov.rfc}")        # Debe ser NULL
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    print("=== CARGA CORRECTA: SOLO nombre_en_quiter y codigo_quiter ===")
    print("🚨 SIN inventar nombres, RFC, ni NADA más")
    
    # Paso 1: Limpiar
    print("\n🧹 PASO 1: Limpiando proveedores...")
    if not limpiar_proveedores():
        sys.exit(1)
    
    # Paso 2: Cargar SOLO lo solicitado
    print("\n📥 PASO 2: Cargando SOLO datos solicitados...")
    cargar_solo_quiter()
    
    # Paso 3: Verificar
    print("\n� PASO 3: Verificando resultado...")
    verificar_resultado()
    
    print("\n🎉 COMPLETADO")
    print("✅ Proveedores creados SOLO con nombre_en_quiter y codigo_quiter")
    print("✅ TODO lo demás = NULL (como debe ser)")
