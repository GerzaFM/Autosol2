#!/usr/bin/env python3
"""
Script de debug para verificar por qué solo sale el primer vale
"""

import sys
import os

# Agregar paths necesarios
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def debug_campo_costos():
    """Debug específico del campo Costos"""
    
    try:
        from ctr_cheque import Cheque
        print("✓ Importación exitosa")
        
        # Datos de prueba
        facturas_test = [
            {
                'folio_interno': 'TEST001',
                'no_vale': 'V1001',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F001',
                'total': 1000.00,
                'iva_trasladado': 160.00,
                'tipo': 'AL'
            },
            {
                'folio_interno': 'TEST002',
                'no_vale': 'V1002',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F002',
                'total': 1500.00,
                'iva_trasladado': 240.00,
                'tipo': 'AL'
            },
            {
                'folio_interno': 'TEST003',
                'no_vale': 'V1003',
                'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
                'rfc_emisor': 'PRT123456789',
                'folio': 'F003',
                'total': 750.00,
                'iva_trasladado': 120.00,
                'tipo': 'AL'
            }
        ]
        
        print("\n🔍 DEBUG PASO A PASO:")
        
        # Paso 1: Verificar consolidación
        print("\n1. Creando instancia temporal...")
        instancia_temp = Cheque(facturas_test[0], "temp.pdf")
        
        print("\n2. Ejecutando consolidación...")
        factura_consolidada = instancia_temp._consolidar_facturas(facturas_test)
        
        print(f"   - Total consolidado: {factura_consolidada.get('total')}")
        print(f"   - IVA consolidado: {factura_consolidada.get('iva_trasladado')}")
        print(f"   - Concepto consolidado: {factura_consolidada.get('concepto_consolidado')}")
        print(f"   - Vales consolidados: {factura_consolidada.get('vales_consolidados')}")
        
        # Paso 2: Crear cheque múltiple
        print("\n3. Creando cheque múltiple...")
        cheque_multiple = Cheque.crear_multiple(facturas_test, "test.pdf")
        
        # Paso 3: Verificar datos del formulario
        print("\n4. Verificando datos del formulario...")
        datos_formulario = cheque_multiple.get_datos_formulario()
        
        print(f"   - Campo Costos: '{datos_formulario.get('Costos')}'")
        print(f"   - Campo Concepto: '{datos_formulario.get('Concepto')}'")
        
        # Paso 4: Verificar la factura interna
        print("\n5. Verificando factura interna...")
        print(f"   - Vales consolidados en factura: {cheque_multiple.factura.get('vales_consolidados')}")
        
        # Paso 5: Debug de la lógica del campo Costos
        print("\n6. Debug de lógica del campo Costos...")
        if cheque_multiple.factura.get('vales_consolidados'):
            vales_lista = cheque_multiple.factura.get('vales_consolidados', [])
            print(f"   - Lista de vales encontrada: {vales_lista}")
            print(f"   - Cantidad de vales: {len(vales_lista)}")
            
            if len(vales_lista) == 1:
                resultado = f"{vales_lista[0]}"
                print(f"   - Resultado (1 vale): '{resultado}'")
            else:
                resultado = f"{' '.join(vales_lista)}"
                print(f"   - Resultado (múltiples vales): '{resultado}'")
        else:
            print("   - No se encontraron vales consolidados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== DEBUG - CAMPO COSTOS ===")
    debug_campo_costos()
    print("\n" + "="*50)
