#!/usr/bin/env python3
"""
Script simplificado para verificar factura existente
"""

import sys
import os

# Agregar rutas para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from src.bd.bd_control import DBManager
    from src.bd.models import Proveedor, Factura, Reparto
    print("✅ Importación exitosa desde src/")
except ImportError:
    try:
        from bd.bd_control import DBManager
        from bd.models import Proveedor, Factura, Reparto
        print("✅ Importación exitosa desde bd/ y solicitudapp/")
    except ImportError as e:
        print(f"❌ Error en importaciones: {e}")
        sys.exit(1)

def main():
    print("🔍 Verificando facturas existentes")
    print("=" * 40)
    
    # Inicializar base de datos
    db_manager = DBManager()
    
    # Verificar facturas existentes
    try:
        facturas = Factura.select()
        print(f"📊 Total de facturas en BD: {facturas.count()}")
        
        if facturas.count() > 0:
            print("\n📋 Facturas encontradas:")
            for i, f in enumerate(facturas, 1):
                print(f"   - Factura {i}:")
                print(f"     Serie: {f.serie}")
                print(f"     Folio: {f.folio}")
                print(f"     Folio interno: {f.folio_interno}")
                try:
                    proveedor_nombre = f.proveedor.nombre if f.proveedor else 'N/A'
                except:
                    proveedor_nombre = 'N/A'
                print(f"     Proveedor: {proveedor_nombre}")
                print(f"     Total: ${f.total}")
                print("   " + "-" * 30)
        else:
            print("📝 No hay facturas en la base de datos.")
            print("💡 Sugerencia: Ejecute la aplicación y cargue un XML primero.")
            
    except Exception as e:
        print(f"❌ Error al consultar facturas: {e}")

if __name__ == "__main__":
    main()
