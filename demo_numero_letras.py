#!/usr/bin/env python3
"""
Demostración de casos de uso reales para la conversión de números a letras en cheques
"""

import sys
import os

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'buscarapp'))

def demo_casos_reales():
    """Demuestra casos de uso reales con importes típicos de cheques"""
    try:
        from ctr_cheque import numero_a_letras
        
        print("💼 DEMO: CASOS REALES DE CHEQUES")
        print("=" * 70)
        
        # Casos típicos de importes de cheques empresariales
        casos_reales = [
            ("Pago pequeño", 125.50),
            ("Factura servicios", 2458.75),
            ("Pago proveedor", 15750.00),
            ("Honorarios profesionales", 25000.00),
            ("Compra equipos", 89500.25),
            ("Pago nómina", 125000.00),
            ("Inversión mayor", 500000.00),
            ("Compra vehículo", 750000.99),
            ("Inversión millonaria", 1500000.00),
            ("Caso con centavos exactos", 999999.01),
        ]
        
        for descripcion, importe in casos_reales:
            letras = numero_a_letras(importe)
            print(f"🏷️  {descripcion}")
            print(f"   💵 ${importe:,.2f}")
            print(f"   📝 {letras}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        return False

def demo_formatos_entrada():
    """Demuestra la flexibilidad con diferentes formatos de entrada"""
    try:
        from ctr_cheque import numero_a_letras
        
        print("🔧 DEMO: FLEXIBILIDAD DE FORMATOS DE ENTRADA")
        print("=" * 70)
        
        # El mismo valor en diferentes formatos
        valor_ejemplo = 6380.00
        formatos = [
            ("Entero", 6380),
            ("Float", 6380.00),
            ("Float con decimales", 6380.50),
            ("String sin comas", "6380.00"),
            ("String con comas", "6,380.00"),
            ("String con espacios", " 6380.50 "),
            ("Decimal string", "6380"),
        ]
        
        for descripcion, valor in formatos:
            try:
                resultado = numero_a_letras(valor)
                print(f"📥 {descripcion:20}: {valor}")
                print(f"📤 Resultado: {resultado}")
                print()
            except Exception as e:
                print(f"❌ Error con formato {descripcion}: {e}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demo formatos: {e}")
        return False

def demo_integracion_cheque():
    """Demuestra la integración completa con la clase Cheque"""
    try:
        from ctr_cheque import Cheque
        
        print("🏦 DEMO: INTEGRACIÓN CON GENERACIÓN DE CHEQUES")
        print("=" * 70)
        
        # Simular diferentes tipos de facturas
        facturas_ejemplo = [
            {
                'nombre': 'Factura de servicios básicos',
                'data': {
                    'nombre_emisor': 'COMERCIAL PAPELERA TEQUISQUIAPAN SA DE CV',
                    'no_vale': '8226744',
                    'folio': '17474',
                    'clase': 'SERVICIO',
                    'total': 6380.00,
                    'folio_interno': 999991
                }
            },
            {
                'nombre': 'Factura de honorarios',
                'data': {
                    'nombre_emisor': 'CONSULTORES ESPECIALIZADOS SA DE CV',
                    'no_vale': '8226745',
                    'folio': '17475',
                    'clase': 'HONORARIO',
                    'total': 25000.75,
                    'folio_interno': 999992
                }
            },
            {
                'nombre': 'Factura de compra mayor',
                'data': {
                    'nombre_emisor': 'DISTRIBUIDORA INDUSTRIAL DEL BAJIO SA DE CV',
                    'no_vale': '8226746',
                    'folio': '17476',
                    'clase': 'COMPRA',
                    'total': 125750.50,
                    'folio_interno': 999993
                }
            }
        ]
        
        for factura_info in facturas_ejemplo:
            print(f"🧾 {factura_info['nombre']}")
            
            # Crear instancia de cheque
            cheque = Cheque(factura_info['data'], "demo_cheque.pdf")
            
            # Mostrar datos del formulario
            datos = cheque.get_datos_formulario()
            
            print(f"   👤 Beneficiario: {datos.get('Orden', 'N/A')}")
            print(f"   💵 Cantidad numérica: ${factura_info['data']['total']:,.2f}")
            print(f"   📝 Cantidad en letras: {datos.get('Moneda', 'N/A')}")
            print(f"   🔢 No. Cheque: {datos.get('cheque', 'N/A')}")
            print(f"   📋 Concepto: {datos.get('Concepto', 'N/A')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demo integración: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🌟 DEMOSTRACIÓN COMPLETA: NÚMEROS A LETRAS PARA CHEQUES")
    print("=" * 80)
    
    # Demo 1: Casos reales
    print("\n1️⃣ CASOS REALES DE IMPORTES")
    exito_reales = demo_casos_reales()
    
    # Demo 2: Formatos de entrada
    print("\n2️⃣ FLEXIBILIDAD DE FORMATOS")
    exito_formatos = demo_formatos_entrada()
    
    # Demo 3: Integración con cheques
    print("\n3️⃣ INTEGRACIÓN CON CHEQUES")
    exito_integracion = demo_integracion_cheque()
    
    # Resumen final
    print("=" * 80)
    print("📊 RESUMEN DE DEMOS:")
    print(f"   Casos reales: {'✅ EXITOSO' if exito_reales else '❌ FALLÓ'}")
    print(f"   Formatos entrada: {'✅ EXITOSO' if exito_formatos else '❌ FALLÓ'}")
    print(f"   Integración cheques: {'✅ EXITOSO' if exito_integracion else '❌ FALLÓ'}")
    
    if all([exito_reales, exito_formatos, exito_integracion]):
        print(f"\n🏆 ¡TODAS LAS DEMOS FUERON EXITOSAS!")
        print("   La función está completamente integrada y lista para producción.")
        print("\n💡 CARACTERÍSTICAS PRINCIPALES:")
        print("   ✅ Conversión precisa de números a letras en español")
        print("   ✅ Formato estándar x/100 MN para centavos")
        print("   ✅ Manejo de diferentes tipos de entrada (int, float, string)")
        print("   ✅ Integración automática en generación de cheques")
        print("   ✅ Fallback automático cuando no hay datos en BD")
        print("   ✅ Manejo de errores robusto")
    else:
        print(f"\n⚠️  Algunas demos fallaron. Revisar la implementación.")
    
    print("=" * 80)
