#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción y guardado de cuentas mayores.
"""

import sys
import os
from pathlib import Path

# Agregar paths para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_extraccion_cuentas_mayores():
    """Prueba la extracción de cuentas mayores de un PDF de orden de compra"""
    try:
        from buscarapp.autocarga.extractor_orden import OrdenDataExtractor
        
        # Buscar archivo PDF de orden de compra en el directorio de pruebas
        test_pdf = "15gerzahin.flores_QRSOPMX208_8226744.pdf"
        
        if not Path(test_pdf).exists():
            print(f"❌ No se encontró el archivo de prueba: {test_pdf}")
            return False
            
        print(f"🔍 Probando extracción de cuentas mayores del archivo: {test_pdf}")
        
        # Crear extractor
        extractor = OrdenDataExtractor()
        
        # Extraer datos completos
        datos = extractor.extract_all_data(test_pdf)
        
        print(f"\n📋 Datos extraídos:")
        for key, value in datos.items():
            if key == 'cuentas_mayores':
                print(f"   💼 {key}: {value} (tipo: {type(value)})")
            else:
                print(f"   📄 {key}: {value}")
        
        # Verificar que se extrajo cuenta mayor
        cuenta_mayor = datos.get('cuentas_mayores')
        if cuenta_mayor:
            print(f"\n✅ Cuenta mayor extraída exitosamente: {cuenta_mayor}")
            print(f"   💼 Tipo de dato: {type(cuenta_mayor)}")
            if isinstance(cuenta_mayor, str) and cuenta_mayor.isdigit():
                print(f"   🎯 Cuenta mayor (para BD): {int(cuenta_mayor)}")
            return True
        else:
            print(f"\n❌ No se encontró cuenta mayor en el PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_simulacion_guardado():
    """Simula el proceso de guardado en base de datos"""
    try:
        # Simular datos de orden como los que llegan al controlador
        orden_data = {
            'Ref_Movimiento': '12345',
            'Cuenta': '1001',
            'Nombre': 'PROVEEDOR TEST',
            'Importe': '1500.00',
            'Importe_en_letras': 'MIL QUINIENTOS PESOS',
            'Codigo_Banco': 'BANAMEX',
            'Folio_Factura': 'F-001',
            'archivo_original': 'test_orden.pdf',
            'cuentas_mayores': '11001234567'  # Ahora es un string directo
        }
        
        print(f"\n🧪 Simulando procesamiento de orden:")
        print(f"   📄 Archivo: {orden_data.get('archivo_original')}")
        print(f"   💼 Cuenta mayor: {orden_data.get('cuentas_mayores')}")
        
        # Simular el procesamiento que hace el controlador
        cuentas_mayores = orden_data.get('cuentas_mayores', None)
        cuenta_mayor = None
        
        if cuentas_mayores:
            if isinstance(cuentas_mayores, str) and cuentas_mayores.isdigit():
                cuenta_mayor = int(cuentas_mayores)
            elif isinstance(cuentas_mayores, int):
                cuenta_mayor = cuentas_mayores
            elif isinstance(cuentas_mayores, (tuple, list)) and len(cuentas_mayores) > 0:
                # Compatibilidad con formato anterior
                cuenta_mayor = int(cuentas_mayores[0]) if str(cuentas_mayores[0]).isdigit() else None
                
        if cuenta_mayor:
            print(f"   ✅ Cuenta mayor procesada para BD: {cuenta_mayor}")
            print(f"   📊 Se guardaría en OrdenCompra.cuenta_mayor = {cuenta_mayor}")
            return True
        else:
            print(f"   ❌ No se pudo procesar la cuenta mayor")
            return False
            
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DE EXTRACCIÓN Y GUARDADO DE CUENTAS MAYORES")
    print("=" * 60)
    
    # Prueba 1: Extracción de PDF real
    print("\n1️⃣ PRUEBA DE EXTRACCIÓN DE PDF:")
    exito_extraccion = test_extraccion_cuentas_mayores()
    
    # Prueba 2: Simulación de guardado
    print("\n2️⃣ PRUEBA DE SIMULACIÓN DE GUARDADO:")
    exito_simulacion = test_simulacion_guardado()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Extracción de PDF: {'✅ EXITOSA' if exito_extraccion else '❌ FALLÓ'}")
    print(f"   Simulación guardado: {'✅ EXITOSA' if exito_simulacion else '❌ FALLÓ'}")
    
    if exito_extraccion and exito_simulacion:
        print("\n🎉 ¡TODAS LAS PRUEBAS FUERON EXITOSAS!")
        print("   La funcionalidad de cuentas mayores está lista para usar.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar la implementación.")
    
    print("=" * 60)
