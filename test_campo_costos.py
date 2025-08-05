#!/usr/bin/env python3
"""
Script de prueba para verificar que el campo Costos muestre todos los vales
"""

import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def test_campo_costos():
    """Prueba específica del campo Costos con múltiples vales"""
    
    try:
        from ctr_cheque import Cheque
        print("✓ Importación de Cheque exitosa")
        
        # Datos de prueba - múltiples facturas con diferentes vales
        facturas_test = [
            {
                'folio_interno': 'TEST001',
                'no_vale': 'V1001',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F001',
                'total': 1000.00,
                'iva_trasladado': 160.00,
                'tipo': 'AL',
                'clase': 'Servicios'
            },
            {
                'folio_interno': 'TEST002',
                'no_vale': 'V1002',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F002',
                'total': 1500.00,
                'iva_trasladado': 240.00,
                'tipo': 'AL',
                'clase': 'Servicios'
            },
            {
                'folio_interno': 'TEST003',
                'no_vale': 'V1003',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F003',
                'total': 750.00,
                'iva_trasladado': 120.00,
                'tipo': 'AL',
                'clase': 'Servicios'
            }
        ]
        
        print("\n🔄 Probando cheque individual...")
        
        # Crear cheque individual para comparar
        cheque_individual = Cheque(facturas_test[0], "test_individual.pdf")
        datos_individual = cheque_individual.get_datos_formulario()
        campo_costos_individual = datos_individual.get('Costos', '')
        
        print(f"✓ Cheque individual - Campo Costos: '{campo_costos_individual}'")
        
        print("\n🔄 Probando cheque múltiple...")
        
        # Crear cheque múltiple
        cheque_multiple = Cheque.crear_multiple(facturas_test, "test_multiple.pdf")
        datos_multiple = cheque_multiple.get_datos_formulario()
        campo_costos_multiple = datos_multiple.get('Costos', '')
        
        print(f"✓ Cheque múltiple - Campo Costos: '{campo_costos_multiple}'")
        
        # Verificar que el campo Costos contiene todos los vales
        vales_esperados = [f['no_vale'] for f in facturas_test]
        print(f"✓ Vales esperados: {vales_esperados}")
        
        # Verificar que cada vale aparece en el campo Costos
        todos_vales_presentes = all(vale in campo_costos_multiple for vale in vales_esperados)
        
        if todos_vales_presentes:
            print("✅ Todos los vales están presentes en el campo Costos")
        else:
            print("❌ Algunos vales no están presentes en el campo Costos")
            for vale in vales_esperados:
                presente = vale in campo_costos_multiple
                print(f"  - {vale}: {'✓' if presente else '❌'}")
        
        # Verificar otros campos importantes
        print(f"\n📋 Otros campos del cheque múltiple:")
        print(f"  - Concepto: '{datos_multiple.get('Concepto', '')}'")
        print(f"  - Cantidad: '{datos_multiple.get('Cantidad', '')}'")
        print(f"  - Orden: '{datos_multiple.get('Orden', '')}'")
        
        # Verificar que se consolidaron correctamente los totales
        total_esperado = sum(f['total'] for f in facturas_test)
        cantidad_campo = datos_multiple.get('Cantidad', '')
        
        print(f"  - Total esperado: ${total_esperado:,.2f}")
        print(f"  - Campo Cantidad: {cantidad_campo}")
        
        return todos_vales_presentes
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== PRUEBA DEL CAMPO COSTOS CON MÚLTIPLES VALES ===\n")
    
    success = test_campo_costos()
    
    if success:
        print("\n🎉 ¡Prueba exitosa! El campo Costos muestra todos los vales correctamente.")
    else:
        print("\n💥 La prueba falló. Revise los errores anteriores.")
    
    print("\n" + "="*60)
