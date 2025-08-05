#!/usr/bin/env python3
"""
Prueba final - verificar campos cheque y Costos con múltiples vales
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def test_final_multiples_vales():
    try:
        from ctr_cheque import Cheque
        print("✓ Importación exitosa")
        
        # Datos similares a los del cheque real (5756, 5768)
        facturas_test = [
            {
                'folio_interno': 'REAL001',
                'no_vale': '5756',
                'nombre_emisor': 'CENTRAL KM 613 COL OLIVAR DE LAS ANIMAS',
                'rfc_emisor': 'TCM220209MQ2',
                'folio': '5756',
                'total': 2310.00,
                'iva_trasladado': 100.00
            },
            {
                'folio_interno': 'REAL002', 
                'no_vale': '5768',
                'nombre_emisor': 'CENTRAL KM 613 COL OLIVAR DE LAS ANIMAS',
                'rfc_emisor': 'TCM220209MQ2',
                'folio': '5768',
                'total': 1500.00,
                'iva_trasladado': 50.00
            }
        ]
        
        print(f"\n📋 Facturas de prueba (simulando caso real):")
        for factura in facturas_test:
            print(f"   - Vale: {factura['no_vale']}, Folio: {factura['folio']}")
        
        # Crear cheque múltiple
        cheque = Cheque.crear_multiple(facturas_test, "cheque_final_test.pdf")
        datos = cheque.get_datos_formulario()
        
        print(f"\n🎯 RESULTADOS:")
        print(f"   - Campo 'cheque': '{datos.get('cheque', 'N/A')}'")
        print(f"   - Campo 'Costos': '{datos.get('Costos', 'N/A')}'")
        print(f"   - Campo 'Concepto': '{datos.get('Concepto', 'N/A')}'")
        print(f"   - Campo 'Cantidad': '{datos.get('Cantidad', 'N/A')}'")
        
        # Verificar que ambos campos contengan ambos vales
        campo_cheque = datos.get('cheque', '')
        campo_costos = datos.get('Costos', '')
        
        print(f"\n✅ VERIFICACIÓN:")
        print(f"   - Campo 'cheque' contiene '5756': {'5756' in campo_cheque}")
        print(f"   - Campo 'cheque' contiene '5768': {'5768' in campo_cheque}")
        print(f"   - Campo 'Costos' contiene '5756': {'5756' in campo_costos}")
        print(f"   - Campo 'Costos' contiene '5768': {'5768' in campo_costos}")
        
        # Generar PDF
        if cheque.exportar():
            print(f"\n📄 PDF generado: cheque_final_test.pdf")
            return True
        else:
            print(f"\n❌ Error generando PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== PRUEBA FINAL - MÚLTIPLES VALES ===")
    success = test_final_multiples_vales()
    
    if success:
        print(f"\n🎉 ¡Prueba exitosa! Ambos campos deberían mostrar los múltiples vales.")
    else:
        print(f"\n💥 Prueba falló.")
    
    print("\n" + "="*50)
