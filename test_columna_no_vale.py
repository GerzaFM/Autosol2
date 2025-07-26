#!/usr/bin/env python3
"""
Test para verificar que la columna No. Vale muestre correctamente los vales asociados
"""
import sys
import os

# Agregar src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from bd.models import Factura, Vale, Proveedor
from buscarapp.controllers.search_controller import SearchController

def test_columna_no_vale():
    print("=== TEST COLUMNA NO. VALE ===")
    
    # 1. Crear controller
    controller = SearchController()
    controller.bd_control = True  # Simular BD disponible
    
    # 2. Cargar facturas
    print("\n1. Cargando facturas...")
    exito = controller.load_facturas()
    
    if not exito:
        print("❌ Error cargando facturas")
        return
    
    # 3. Obtener facturas de NAVA MEDRANO específicamente
    facturas_data = controller.state.all_facturas
    facturas_nava = [f for f in facturas_data if 'NAVA' in f.get('nombre_emisor', '')]
    
    print(f"✅ Total facturas: {len(facturas_data)}")
    print(f"✅ Facturas NAVA: {len(facturas_nava)}")
    
    # 4. Verificar columna no_vale para facturas NAVA
    print(f"\n2. VERIFICANDO COLUMNA NO. VALE:")
    for factura in facturas_nava:
        folio = factura.get('folio_interno', '')
        nombre = factura.get('nombre_emisor', '')
        no_vale = factura.get('no_vale', '')
        
        print(f"   📄 Factura {folio}: {nombre}")
        print(f"      💳 No. Vale: '{no_vale}'")
        
        # Verificar en BD directamente
        try:
            vale_db = Vale.get(Vale.factura_id == int(folio))
            print(f"      ✅ Vale en BD: {vale_db.noVale}")
            if no_vale == vale_db.noVale:
                print(f"      ✅ CORRECTO - Coincide con BD")
            else:
                print(f"      ❌ INCORRECTO - BD: {vale_db.noVale}, Tabla: {no_vale}")
        except Vale.DoesNotExist:
            print(f"      ⚠️ Sin vale en BD")
            if no_vale == "":
                print(f"      ✅ CORRECTO - Vacío como esperado")
            else:
                print(f"      ❌ INCORRECTO - Debería estar vacío")
        print()
    
    # 5. Mostrar algunas facturas con vales
    print(f"\n3. FACTURAS CON VALES (MUESTRA):")
    facturas_con_vales = [f for f in facturas_data if f.get('no_vale', '') != '']
    
    print(f"   Total facturas con vales: {len(facturas_con_vales)}")
    for factura in facturas_con_vales[:5]:  # Solo primeras 5
        folio = factura.get('folio_interno', '')
        nombre = factura.get('nombre_emisor', '')[:30] + "..." if len(factura.get('nombre_emisor', '')) > 30 else factura.get('nombre_emisor', '')
        no_vale = factura.get('no_vale', '')
        
        print(f"   📄 {folio} | {nombre} | Vale: {no_vale}")

if __name__ == "__main__":
    test_columna_no_vale()
