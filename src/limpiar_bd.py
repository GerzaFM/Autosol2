#!/usr/bin/env python3
"""
Script para limpiar la base de datos de prueba.
Elimina todos los datos de ejemplo y registros de prueba.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def limpiar_base_datos():
    """Limpia todos los datos de la base de datos de manera segura."""
    try:
        from bd.models import (
            Factura, Proveedor, Concepto, Reparto, Vale, OrdenCompra, 
            Banco, Usuario, RepartoFavorito, Layout, db
        )
        
        print("🧹 Iniciando limpieza de la base de datos...")
        
        # Conectar a la base de datos
        if not db.is_connection_usable():
            # Buscar la base de datos en diferentes ubicaciones
            db_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'facturas.db'),
                os.path.join(os.path.dirname(__file__), 'facturas.db'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'facturas.db')
            ]
            
            db_found = False
            for db_path in db_paths:
                abs_path = os.path.abspath(db_path)
                if os.path.exists(abs_path):
                    print(f"📂 Base de datos encontrada en: {abs_path}")
                    db.init(abs_path)
                    db_found = True
                    break
            
            if not db_found:
                print("❌ No se encontró la base de datos facturas.db")
                return False
        
        # Mostrar estadísticas antes de limpiar
        print("\n📊 Estadísticas antes de la limpieza:")
        try:
            print(f"   Facturas: {Factura.select().count()}")
            print(f"   Proveedores: {Proveedor.select().count()}")
            print(f"   Conceptos: {Concepto.select().count()}")
            print(f"   Repartos: {Reparto.select().count()}")
            print(f"   Vales: {Vale.select().count()}")
            print(f"   Órdenes de Compra: {OrdenCompra.select().count()}")
            print(f"   Bancos: {Banco.select().count()}")
            print(f"   Usuarios: {Usuario.select().count()}")
            print(f"   Repartos Favoritos: {RepartoFavorito.select().count()}")
            print(f"   Layouts: {Layout.select().count()}")
        except Exception as e:
            print(f"   No se pudieron obtener estadísticas: {e}")
        
        # Confirmar limpieza
        respuesta = input("\n⚠️  ¿Está seguro de que desea eliminar TODOS los datos? (escriba 'SI' para confirmar): ")
        if respuesta != 'SI':
            print("❌ Operación cancelada")
            return False
        
        print("\n🗑️  Eliminando datos en orden de dependencias...")
        
        # Eliminar en orden de dependencias (de hijos a padres)
        eliminados = {}
        
        # 1. Repartos Favoritos (depende de Usuario)
        try:
            count = RepartoFavorito.delete().execute()
            eliminados['RepartoFavorito'] = count
            print(f"   ✅ Repartos Favoritos eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Repartos Favoritos: {e}")
        
        # 2. Órdenes de Compra (depende de Factura)
        try:
            count = OrdenCompra.delete().execute()
            eliminados['OrdenCompra'] = count
            print(f"   ✅ Órdenes de Compra eliminadas: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Órdenes de Compra: {e}")
        
        # 3. Conceptos (depende de Factura)
        try:
            count = Concepto.delete().execute()
            eliminados['Concepto'] = count
            print(f"   ✅ Conceptos eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Conceptos: {e}")
        
        # 4. Repartos (depende de Factura)
        try:
            count = Reparto.delete().execute()
            eliminados['Reparto'] = count
            print(f"   ✅ Repartos eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Repartos: {e}")
        
        # 5. Vales (depende de Factura)
        try:
            count = Vale.delete().execute()
            eliminados['Vale'] = count
            print(f"   ✅ Vales eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Vales: {e}")
        
        # 6. Facturas (depende de Proveedor y Layout)
        try:
            count = Factura.delete().execute()
            eliminados['Factura'] = count
            print(f"   ✅ Facturas eliminadas: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Facturas: {e}")
        
        # 7. Usuarios (independiente, pero Usuario puede depender de sí mismo)
        try:
            count = Usuario.delete().execute()
            eliminados['Usuario'] = count
            print(f"   ✅ Usuarios eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Usuarios: {e}")
        
        # 8. Bancos (independiente)
        try:
            count = Banco.delete().execute()
            eliminados['Banco'] = count
            print(f"   ✅ Bancos eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Bancos: {e}")
        
        # 9. Layouts (independiente)
        try:
            count = Layout.delete().execute()
            eliminados['Layout'] = count
            print(f"   ✅ Layouts eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Layouts: {e}")
        
        # 10. Proveedores (independiente)
        try:
            count = Proveedor.delete().execute()
            eliminados['Proveedor'] = count
            print(f"   ✅ Proveedores eliminados: {count}")
        except Exception as e:
            print(f"   ⚠️  Error eliminando Proveedores: {e}")
        
        # Resumen final
        print("\n📊 Resumen de limpieza:")
        total_eliminados = sum(eliminados.values())
        for tabla, count in eliminados.items():
            print(f"   {tabla}: {count} registros")
        print(f"   TOTAL: {total_eliminados} registros eliminados")
        
        # Verificar que las tablas están vacías
        print("\n🔍 Verificando limpieza...")
        try:
            print(f"   Facturas restantes: {Factura.select().count()}")
            print(f"   Proveedores restantes: {Proveedor.select().count()}")
            print(f"   Conceptos restantes: {Concepto.select().count()}")
            print(f"   Repartos restantes: {Reparto.select().count()}")
            print(f"   Vales restantes: {Vale.select().count()}")
        except Exception as e:
            print(f"   Error verificando: {e}")
        
        print("\n✅ Base de datos limpiada exitosamente")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧹 SCRIPT DE LIMPIEZA DE BASE DE DATOS")
    print("=" * 50)
    print("Este script eliminará TODOS los datos de la base de datos.")
    print("Use con precaución - esta operación NO se puede deshacer.")
    print("=" * 50)
    
    if limpiar_base_datos():
        print("\n🎉 Limpieza completada exitosamente")
    else:
        print("\n💥 La limpieza falló o fue cancelada")
