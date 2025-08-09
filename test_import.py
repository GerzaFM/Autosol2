#!/usr/bin/env python3
"""
Script de prueba rápida para verificar la importación
"""

import sys
import os

# Agregar las rutas necesarias
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'buscarapp'))

def test_import():
    try:
        from buscarapp.ctr_cheque import Cheque
        print("✅ Importación de Cheque exitosa")
        
        # Datos de prueba mínimos (2 facturas para activar reporte)
        facturas_test = [
            {
                'id': 1,
                'proveedor': 'TEST PROVEEDOR',
                'no_vale': 'V001',
                'folio': 'F001',
                'conceptos': 'Prueba 1',
                'importe': 1000.0,
                'iva': 160.0,
                'ret_iva': 16.0,
                'ret_isr': 100.0,
                'total': 1044.0,
                'subtotal': 1000.0,
                'iva_trasladado': 160.0,
                'nombre_emisor': 'TEST PROVEEDOR'
            },
            {
                'id': 2,
                'proveedor': 'TEST PROVEEDOR',
                'no_vale': 'V002',
                'folio': 'F002',
                'conceptos': 'Prueba 2',
                'importe': 2000.0,
                'iva': 320.0,
                'ret_iva': 32.0,
                'ret_isr': 200.0,
                'total': 2088.0,
                'subtotal': 2000.0,
                'iva_trasladado': 320.0,
                'nombre_emisor': 'TEST PROVEEDOR'
            }
        ]
        
        ruta_prueba = os.path.join(os.getcwd(), "test_import.pdf")
        print(f"🔄 Probando crear_multiple con 2 facturas...")
        
        cheque = Cheque.crear_multiple(facturas_test, ruta_prueba, generar_reporte=True)
        print("✅ crear_multiple exitoso")
        
        # Intentar exportar
        if cheque.exportar():
            print("✅ Exportación exitosa")
        else:
            print("❌ Error en exportación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()
