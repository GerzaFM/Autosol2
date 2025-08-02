#!/usr/bin/env python3
"""
Script de prueba para la función de conversión de números a letras
"""

import sys
import os

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def test_numero_a_letras():
    """Prueba la función de conversión de números a letras"""
    try:
        from ctr_cheque import numero_a_letras
        
        # Casos de prueba
        casos_prueba = [
            (0, "CERO PESOS 00/100 MN"),
            (1, "UNO PESOS 00/100 MN"),
            (15, "QUINCE PESOS 00/100 MN"),
            (25, "VEINTICINCO PESOS 00/100 MN"),
            (100, "CIEN PESOS 00/100 MN"),
            (101, "CIENTO UNO PESOS 00/100 MN"),
            (200, "DOSCIENTOS PESOS 00/100 MN"),
            (1000, "MIL PESOS 00/100 MN"),
            (1001, "MIL UNO PESOS 00/100 MN"),
            (1234, "MIL DOSCIENTOS TREINTA Y CUATRO PESOS 00/100 MN"),
            (1234.56, "MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 MN"),
            (0.75, "CERO PESOS 75/100 MN"),
            (10000, "DIEZ MIL PESOS 00/100 MN"),
            (50000.25, "CINCUENTA MIL PESOS 25/100 MN"),
            (1000000, "UN MILLÓN PESOS 00/100 MN"),
            (1234567.89, "UN MILLÓN DOSCIENTOS TREINTA Y CUATRO MIL QUINIENTOS SESENTA Y SIETE PESOS 89/100 MN"),
            ("6,380.00", "SEIS MIL TRESCIENTOS OCHENTA PESOS 00/100 MN"),
            ("1,500", "MIL QUINIENTOS PESOS 00/100 MN"),
        ]
        
        print("🧪 PRUEBAS DE CONVERSIÓN DE NÚMEROS A LETRAS")
        print("=" * 80)
        
        exitosos = 0
        errores = 0
        
        for numero, esperado in casos_prueba:
            try:
                resultado = numero_a_letras(numero)
                
                if "ERROR EN CONVERSIÓN" not in resultado:
                    print(f"✅ {numero:>12} → {resultado}")
                    exitosos += 1
                else:
                    print(f"❌ {numero:>12} → {resultado}")
                    errores += 1
                    
            except Exception as e:
                print(f"❌ {numero:>12} → Error: {e}")
                errores += 1
        
        print("=" * 80)
        print(f"📊 RESUMEN: {exitosos} exitosos, {errores} errores")
        
        # Casos especiales y edge cases
        print(f"\n🔍 CASOS ESPECIALES:")
        casos_especiales = [21, 30, 99, 121, 999, 2000, 21000, 100000, 999999]
        
        for numero in casos_especiales:
            resultado = numero_a_letras(numero)
            print(f"   {numero:>6} → {resultado}")
        
        return exitosos > errores
        
    except ImportError as e:
        print(f"❌ Error importando la función: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False

def test_integración_cheque():
    """Prueba la integración con la clase Cheque"""
    try:
        from ctr_cheque import Cheque
        
        # Simular datos de factura
        factura_prueba = {
            'nombre_emisor': 'PROVEEDOR TEST SA DE CV',
            'no_vale': '12345',
            'folio': 'F-001',
            'clase': 'SERVICIO',
            'total': 6380.00,
            'folio_interno': 999999  # Folio que no existe en BD
        }
        
        print(f"\n🔧 PRUEBA DE INTEGRACIÓN CON CLASE CHEQUE")
        print("=" * 50)
        
        # Crear instancia de cheque (sin generar archivo)
        cheque = Cheque(factura_prueba, "test_cheque.pdf")
        
        # Probar conversión directa
        importe_letras = cheque.convertir_numero_a_letras(6380.00)
        print(f"💰 Importe original: $6,380.00")
        print(f"📝 Importe en letras: {importe_letras}")
        
        # Verificar que los datos del formulario incluyen el importe en letras
        datos_formulario = cheque.get_datos_formulario()
        print(f"🏛️ Campo 'Moneda' en formulario: {datos_formulario.get('Moneda', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE CONVERSIÓN NÚMEROS A LETRAS")
    print("=" * 80)
    
    # Prueba 1: Función básica
    exito_funcion = test_numero_a_letras()
    
    # Prueba 2: Integración con clase
    exito_integracion = test_integración_cheque()
    
    # Resumen final
    print(f"\n" + "=" * 80)
    print("📊 RESUMEN FINAL:")
    print(f"   Función básica: {'✅ EXITOSA' if exito_funcion else '❌ FALLÓ'}")
    print(f"   Integración cheque: {'✅ EXITOSA' if exito_integracion else '❌ FALLÓ'}")
    
    if exito_funcion and exito_integracion:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS FUERON EXITOSAS!")
        print("   La función de conversión está lista para usar en los cheques.")
    else:
        print(f"\n⚠️  Algunas pruebas fallaron. Revisar la implementación.")
    
    print("=" * 80)
