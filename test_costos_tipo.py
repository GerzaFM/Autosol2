#!/usr/bin/env python3
"""
Prueba para verificar que el campo Costos muestre el tipo de vale
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def test_campo_costos_tipo_vale():
    try:
        from ctr_cheque import Cheque
        print("✓ Importación exitosa")
        
        # Datos de prueba con tipo de vale
        facturas_test = [
            {
                'folio_interno': 'TEST001',
                'no_vale': '5756',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': '5756',
                'total': 1000.00,
                'iva_trasladado': 160.00,
                'tipo': 'AL'  # Código del tipo de vale
            },
            {
                'folio_interno': 'TEST002',
                'no_vale': '5768',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': '5768',
                'total': 1500.00,
                'iva_trasladado': 240.00,
                'tipo': 'AL'  # Mismo tipo de vale
            }
        ]
        
        print(f"\n📋 Probando cheque individual:")
        cheque_individual = Cheque(facturas_test[0], "test_individual.pdf")
        datos_individual = cheque_individual.get_datos_formulario()
        print(f"   - Campo Costos: '{datos_individual.get('Costos', 'N/A')}'")
        
        print(f"\n📋 Probando cheque múltiple:")
        cheque_multiple = Cheque.crear_multiple(facturas_test, "test_multiple.pdf")
        datos_multiple = cheque_multiple.get_datos_formulario()
        
        print(f"   - Campo 'cheque': '{datos_multiple.get('cheque', 'N/A')}'")
        print(f"   - Campo 'Costos': '{datos_multiple.get('Costos', 'N/A')}'")
        print(f"   - Campo 'Concepto': '{datos_multiple.get('Concepto', 'N/A')}'")
        
        # Verificar que Costos muestre el tipo de vale, no los números
        campo_costos = datos_multiple.get('Costos', '')
        contiene_numeros_vale = any(vale in campo_costos for vale in ['5756', '5768'])
        contiene_tipo_vale = 'AL' in campo_costos or 'ALIMENTACIÓN' in campo_costos.upper()
        
        print(f"\n✅ VERIFICACIÓN:")
        print(f"   - Contiene números de vale: {contiene_numeros_vale} (debería ser False)")
        print(f"   - Contiene tipo de vale: {contiene_tipo_vale} (debería ser True)")
        
        if not contiene_numeros_vale and contiene_tipo_vale:
            print(f"   🎉 ¡CORRECTO! El campo Costos muestra el tipo de vale, no los números")
            return True
        else:
            print(f"   ❌ ERROR: El campo Costos no está mostrando correctamente el tipo de vale")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== PRUEBA CAMPO COSTOS - TIPO DE VALE ===")
    success = test_campo_costos_tipo_vale()
    
    if success:
        print(f"\n🎉 ¡Prueba exitosa! El campo Costos ahora muestra el tipo de vale correctamente.")
    else:
        print(f"\n💥 La prueba falló.")
    
    print("\n" + "="*50)
