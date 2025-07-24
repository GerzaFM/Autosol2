#!/usr/bin/env python3
"""
Script para probar la corrección del error SQL en buscar_app.py
"""

import sys
import os
from pathlib import Path

# Configurar rutas
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_sql_fix():
    """Prueba la corrección del error SQL."""
    print("🧪 Prueba de corrección del error SQL")
    print("=" * 40)
    
    try:
        # Cambiar al directorio src para importaciones correctas
        os.chdir(str(PROJECT_ROOT / "src"))
        
        # Importar las clases necesarias
        from bd.bd_control import DBManager
        from bd.models import Factura, Proveedor, Vale
        
        print("✅ Modelos importados correctamente")
        
        # Inicializar base de datos
        db_manager = DBManager()
        print("✅ Base de datos inicializada")
        
        # Probar la consulta que estaba fallando
        print("🔍 Probando consulta SQL corregida...")
        
        facturas_query = (Factura
                         .select()
                         .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                         .switch(Factura)
                         .join(Vale, join_type='LEFT OUTER', on=(Vale.factura == Factura.folio_interno))
                         .order_by(Factura.fecha.desc()))
        
        # Intentar ejecutar la consulta
        facturas_count = 0
        for factura in facturas_query:
            facturas_count += 1
            if facturas_count <= 3:  # Mostrar solo las primeras 3
                print(f"   - Factura {factura.folio_interno}: {factura.serie}-{factura.folio}")
                print(f"     Proveedor: {factura.proveedor.nombre}")
                try:
                    if hasattr(factura, 'vale') and factura.vale:
                        print(f"     Vale: {factura.vale.noVale}")
                    else:
                        print("     Vale: Sin vale asociado")
                except:
                    print("     Vale: Sin vale asociado")
        
        print(f"✅ Consulta SQL ejecutada exitosamente")
        print(f"📊 Total de facturas encontradas: {facturas_count}")
        
        if facturas_count == 0:
            print("💡 No hay facturas en la base de datos")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 CORRECCIÓN EXITOSA")
    print("El error SQL 'near AS: syntax error' ha sido resuelto")
    return True

if __name__ == "__main__":
    test_sql_fix()
