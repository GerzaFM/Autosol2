#!/usr/bin/env python3
"""
Script para verificar y actualizar la estructura de la tabla proveedor
"""

import sys
import os

# Agregar paths para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def verificar_y_actualizar_tabla_proveedor():
    """Verifica y actualiza la estructura de la tabla proveedor"""
    try:
        from bd.models import db, Proveedor
        
        print("🔍 VERIFICANDO ESTRUCTURA DE TABLA PROVEEDOR")
        print("=" * 60)
        
        # Conectar a la base de datos
        db.connect()
        
        # Verificar si la tabla existe
        if not Proveedor.table_exists():
            print("❌ La tabla proveedor no existe. Creándola...")
            db.create_tables([Proveedor])
            print("✅ Tabla proveedor creada exitosamente")
        else:
            print("✅ La tabla proveedor existe")
        
        # Obtener estructura actual de la tabla
        cursor = db.execute_sql("PRAGMA table_info(proveedor)")
        columnas_existentes = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Columnas existentes en BD: {columnas_existentes}")
        
        # Verificar si falta la columna cuenta_mayor
        if 'cuenta_mayor' not in columnas_existentes:
            print("⚠️ La columna cuenta_mayor no existe. Agregándola...")
            
            # Agregar la columna cuenta_mayor
            db.execute_sql("ALTER TABLE proveedor ADD COLUMN cuenta_mayor INTEGER")
            print("✅ Columna cuenta_mayor agregada exitosamente")
        else:
            print("✅ La columna cuenta_mayor ya existe")
        
        # Verificar estructura final
        cursor = db.execute_sql("PRAGMA table_info(proveedor)")
        columnas_finales = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Estructura final: {columnas_finales}")
        
        # Probar una consulta simple
        print("\n🧪 PROBANDO CONSULTAS:")
        
        # Contar proveedores sin cuenta mayor
        proveedores_sin_cuenta = Proveedor.select().where(
            (Proveedor.cuenta_mayor.is_null()) | 
            (Proveedor.cuenta_mayor == 0)
        ).count()
        
        print(f"   📊 Proveedores sin cuenta mayor: {proveedores_sin_cuenta}")
        
        # Contar proveedores con cuenta mayor
        proveedores_con_cuenta = Proveedor.select().where(
            (Proveedor.cuenta_mayor.is_null(False)) & 
            (Proveedor.cuenta_mayor != 0)
        ).count()
        
        print(f"   📊 Proveedores con cuenta mayor: {proveedores_con_cuenta}")
        
        # Mostrar algunos ejemplos
        print(f"\n📄 EJEMPLOS DE PROVEEDORES:")
        proveedores_ejemplo = Proveedor.select().limit(3)
        
        for proveedor in proveedores_ejemplo:
            print(f"   👤 {proveedor.nombre}")
            print(f"      🔢 Código Quiter: {proveedor.codigo_quiter}")
            print(f"      🏦 Cuenta Mayor: {proveedor.cuenta_mayor}")
            print()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_actualizacion_cuenta_mayor():
    """Prueba la actualización de cuenta mayor en un proveedor"""
    try:
        from bd.models import db, Proveedor
        from bd.bd_control import BDControl
        
        print("\n🧪 PRUEBA DE ACTUALIZACIÓN DE CUENTA MAYOR")
        print("=" * 50)
        
        db.connect()
        
        # Buscar un proveedor sin cuenta mayor
        proveedor = Proveedor.select().where(
            (Proveedor.cuenta_mayor.is_null()) | 
            (Proveedor.cuenta_mayor == 0)
        ).first()
        
        if proveedor:
            print(f"👤 Proveedor seleccionado: {proveedor.nombre}")
            print(f"🏦 Cuenta mayor actual: {proveedor.cuenta_mayor}")
            
            # Probar actualización
            cuenta_mayor_test = 23020000152
            proveedor.cuenta_mayor = cuenta_mayor_test
            proveedor.save()
            
            print(f"✅ Cuenta mayor actualizada a: {cuenta_mayor_test}")
            
            # Verificar la actualización
            proveedor_verificacion = Proveedor.get(Proveedor.id == proveedor.id)
            print(f"🔍 Verificación - Cuenta mayor: {proveedor_verificacion.cuenta_mayor}")
            
            # Restaurar estado original
            proveedor.cuenta_mayor = None
            proveedor.save()
            print(f"🔄 Estado restaurado (cuenta mayor: {proveedor.cuenta_mayor})")
            
        else:
            print("⚠️ No se encontró proveedor sin cuenta mayor para prueba")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE TABLA PROVEEDOR")
    print("=" * 80)
    
    # Verificar y actualizar estructura
    exito_estructura = verificar_y_actualizar_tabla_proveedor()
    
    # Probar funcionalidad
    exito_prueba = test_actualizacion_cuenta_mayor() if exito_estructura else False
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN:")
    print(f"   Estructura BD: {'✅ CORRECTA' if exito_estructura else '❌ ERROR'}")
    print(f"   Prueba funcional: {'✅ EXITOSA' if exito_prueba else '❌ FALLÓ'}")
    
    if exito_estructura and exito_prueba:
        print(f"\n🎉 ¡TABLA PROVEEDOR LISTA PARA USAR!")
        print("   El campo cuenta_mayor está disponible y funcional.")
    else:
        print(f"\n⚠️  Revisar errores antes de continuar.")
    
    print("=" * 80)
