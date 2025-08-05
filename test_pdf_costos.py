#!/usr/bin/env python3
"""
Script para verificar que el campo Costos se pasa correctamente al PDF
"""

import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def test_costos_en_pdf():
    """Prueba específica de cómo se ve el campo Costos en el formulario"""
    
    try:
        from ctr_cheque import Cheque
        print("✓ Importación exitosa")
        
        # Datos de prueba con múltiples vales
        facturas_test = [
            {
                'folio_interno': 'TEST001',
                'no_vale': 'V5756',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': '5756',
                'total': 1000.00,
                'iva_trasladado': 160.00
            },
            {
                'folio_interno': 'TEST002',
                'no_vale': 'V5768',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': '5768',
                'total': 1500.00,
                'iva_trasladado': 240.00
            }
        ]
        
        print(f"\n📋 Facturas de prueba:")
        for i, factura in enumerate(facturas_test, 1):
            print(f"   {i}. Vale: {factura['no_vale']}, Folio: {factura['folio']}, Total: ${factura['total']}")
        
        # Crear cheque múltiple
        print(f"\n🔄 Creando cheque múltiple...")
        cheque_multiple = Cheque.crear_multiple(facturas_test, "test_costos_multiples.pdf")
        
        # Obtener todos los datos del formulario
        datos_formulario = cheque_multiple.get_datos_formulario()
        
        print(f"\n📊 Datos del formulario completos:")
        for campo, valor in datos_formulario.items():
            if campo == 'Costos':
                print(f"   🎯 {campo}: '{valor}' (longitud: {len(str(valor))} caracteres)")
            else:
                valor_display = str(valor)[:50] + "..." if len(str(valor)) > 50 else str(valor)
                print(f"   - {campo}: '{valor_display}'")
        
        # Verificación específica del campo Costos
        campo_costos = datos_formulario.get('Costos', '')
        print(f"\n🔍 Análisis del campo Costos:")
        print(f"   - Valor: '{campo_costos}'")
        print(f"   - Longitud: {len(campo_costos)} caracteres")
        print(f"   - Contiene V5756: {'V5756' in campo_costos}")
        print(f"   - Contiene V5768: {'V5768' in campo_costos}")
        
        # Verificar si se genera el PDF correctamente
        print(f"\n📄 Generando PDF de prueba...")
        try:
            resultado = cheque_multiple.exportar()
            if resultado:
                print(f"   ✅ PDF generado exitosamente")
                
                # Verificar que el archivo existe
                if os.path.exists("test_costos_multiples.pdf"):
                    size = os.path.getsize("test_costos_multiples.pdf")
                    print(f"   📁 Archivo creado: {size} bytes")
                    print(f"   📍 Ruta: {os.path.abspath('test_costos_multiples.pdf')}")
                else:
                    print(f"   ⚠️  Archivo no encontrado")
            else:
                print(f"   ❌ Error generando PDF")
        except Exception as pdf_error:
            print(f"   ⚠️  Error en PDF: {pdf_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== PRUEBA CAMPO COSTOS EN PDF ===")
    success = test_costos_en_pdf()
    
    if success:
        print(f"\n🎉 Prueba completada. Revise el PDF generado para ver si el campo Costos muestra ambos vales.")
        print(f"   - Si solo muestra un vale, el problema está en el formulario PDF")
        print(f"   - Si muestra ambos vales, el problema era en la aplicación")
    else:
        print(f"\n💥 La prueba falló.")
    
    print("\n" + "="*60)
