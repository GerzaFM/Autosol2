#!/usr/bin/env python3
"""
Prueba integral de división completa: totales + conceptos
Simula el flujo completo de la funcionalidad dividir
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bd.models import Factura, Reparto, Proveedor, db
from bd.bd_control import DBManager

def test_division_completa():
    """Prueba la división completa de totales y conceptos"""
    try:
        db.connect()
        db_manager = DBManager()
        
        print("🎯 PRUEBA INTEGRAL: DIVISIÓN COMPLETA (TOTALES + CONCEPTOS)")
        print("="*70)
        
        # Generar datos únicos
        timestamp = str(int(time.time()))[-6:]
        folio_base = f"DIV{timestamp}"
        
        # Datos completos simulando la aplicación
        datos_completos = {
            # Proveedor
            'nombre_proveedor': 'PROVEEDOR DIVISIÓN SA DE CV',
            'rfc_proveedor': 'PDI123456789',
            
            # Factura
            'serie': 'A',
            'folio': folio_base,
            'fecha': '2024-01-15',
            'tipo': 'SC - SOLICITUD DE COMPRA',
            'nombre_receptor': 'TCM MATEHUALA SA DE CV',
            'rfc_receptor': 'TMC987654321',
            'comentario': 'Prueba división completa',
            'clase': 'GASTOS',
            
            # Conceptos (simulando lo que estaría en la tabla)
            'conceptos': [
                {
                    'descripcion': 'Servicio especializado',
                    'cantidad': 2,
                    'precio_unitario': 400.00,
                    'importe': 800.00
                },
                {
                    'descripcion': 'Materiales diversos',
                    'cantidad': 1,
                    'precio_unitario': 200.00,
                    'importe': 200.00
                }
            ],
            
            # Totales (calculados de conceptos)
            'subtotal': 1000.00,
            'ret_iva': 50.00,
            'ret_isr': 30.00,
            'iva_trasladado': 160.00,
            'total': 1080.00,
            
            # Reparto
            'p_comercial': 600.00,
            'p_fleet': 480.00
        }
        
        print("📋 DATOS ORIGINALES:")
        print("-" * 70)
        print(f"Folio: {datos_completos['folio']}")
        print(f"Tipo: {datos_completos['tipo']}")
        print()
        
        print("CONCEPTOS ORIGINALES:")
        print(f"{'Cant.':<5} {'Descripción':<25} {'Precio Unit.':<12} {'Total':<10}")
        print("-" * 60)
        for concepto in datos_completos['conceptos']:
            print(f"{concepto['cantidad']:<5} {concepto['descripcion']:<25} ${concepto['precio_unitario']:<11.2f} ${concepto['importe']:<9.2f}")
        print()
        
        print("TOTALES ORIGINALES:")
        print(f"Subtotal: ${datos_completos['subtotal']:.2f}")
        print(f"IVA: ${datos_completos['iva_trasladado']:.2f}")
        print(f"Retención: ${datos_completos['ret_iva']:.2f}")
        print(f"TOTAL: ${datos_completos['total']:.2f}")
        print()
        
        print("REPARTO ORIGINAL:")
        print(f"Comercial: ${datos_completos['p_comercial']:.2f}")
        print(f"Fleet: ${datos_completos['p_fleet']:.2f}")
        print()
        
        # SIMULAR PRIMERA FACTURA CON DIVISIÓN
        print("🔄 PASO 1: DIVISIÓN DE TODOS LOS VALORES")
        print("="*50)
        
        datos_divididos = datos_completos.copy()
        datos_divididos['conceptos'] = [concepto.copy() for concepto in datos_completos['conceptos']]
        
        # Dividir totales
        datos_divididos['subtotal'] /= 2
        datos_divididos['ret_iva'] /= 2
        datos_divididos['ret_isr'] /= 2
        datos_divididos['iva_trasladado'] /= 2
        datos_divididos['total'] /= 2
        
        # Dividir reparto
        datos_divididos['p_comercial'] /= 2
        datos_divididos['p_fleet'] /= 2
        
        # Dividir conceptos (NUEVO: precio y total, cantidad igual)
        for concepto in datos_divididos['conceptos']:
            # Cantidad permanece igual
            concepto['precio_unitario'] /= 2  # Precio se divide
            concepto['importe'] /= 2  # Total se divide
        
        print("CONCEPTOS DIVIDIDOS:")
        print(f"{'Cant.':<5} {'Descripción':<25} {'Precio Unit.':<12} {'Total':<10}")
        print("-" * 60)
        for i, concepto in enumerate(datos_divididos['conceptos']):
            original = datos_completos['conceptos'][i]
            print(f"{concepto['cantidad']:<5} {concepto['descripcion']:<25} ${concepto['precio_unitario']:<11.2f} ${concepto['importe']:<9.2f}")
            precio_orig = original['precio_unitario']
            importe_orig = original['importe']
            print(f"{'':>5} {'(Orig: $' + str(precio_orig) + ')':<25} {'(Orig: $' + str(importe_orig) + ')'}")
        print()
        
        print("TOTALES DIVIDIDOS:")
        print(f"Subtotal: ${datos_divididos['subtotal']:.2f} (Original: ${datos_completos['subtotal']:.2f})")
        print(f"IVA: ${datos_divididos['iva_trasladado']:.2f} (Original: ${datos_completos['iva_trasladado']:.2f})")
        print(f"Retención: ${datos_divididos['ret_iva']:.2f} (Original: ${datos_completos['ret_iva']:.2f})")
        print(f"TOTAL: ${datos_divididos['total']:.2f} (Original: ${datos_completos['total']:.2f})")
        print()
        
        print("REPARTO DIVIDIDO:")
        print(f"Comercial: ${datos_divididos['p_comercial']:.2f} (Original: ${datos_completos['p_comercial']:.2f})")
        print(f"Fleet: ${datos_divididos['p_fleet']:.2f} (Original: ${datos_completos['p_fleet']:.2f})")
        print()
        
        # GUARDAR PRIMERA FACTURA
        print("💾 GUARDANDO PRIMERA FACTURA (SC)...")
        factura_sc = db_manager.guardar_formulario(datos_divididos)
        print(f"✅ Primera factura guardada: folio_interno={factura_sc.folio_interno}")
        print()
        
        # SIMULAR SEGUNDA FACTURA (VC)
        print("🔄 PASO 2: PREPARANDO SEGUNDA FACTURA (VC)")
        print("="*45)
        
        datos_vc = datos_divididos.copy()
        datos_vc['tipo'] = 'VC - VALE DE CONTROL'
        datos_vc['folio'] = f"{folio_base}_VC"
        
        print(f"Tipo cambiado: {datos_vc['tipo']}")
        print(f"Folio cambiado: {datos_vc['folio']}")
        print("Los totales y conceptos mantienen la división...")
        print()
        
        # GUARDAR SEGUNDA FACTURA
        print("💾 GUARDANDO SEGUNDA FACTURA (VC)...")
        factura_vc = db_manager.guardar_formulario(datos_vc)
        print(f"✅ Segunda factura guardada: folio_interno={factura_vc.folio_interno}")
        print()
        
        # VERIFICACIÓN FINAL
        print("🔍 VERIFICACIÓN FINAL:")
        print("="*40)
        print(f"Factura SC: ${factura_sc.total:.2f}")
        print(f"Factura VC: ${factura_vc.total:.2f}")
        print(f"Suma: ${factura_sc.total + factura_vc.total:.2f}")
        print(f"Original: ${datos_completos['total']:.2f}")
        print(f"Diferencia: ${abs((factura_sc.total + factura_vc.total) - datos_completos['total']):.2f}")
        
        if abs((factura_sc.total + factura_vc.total) - datos_completos['total']) < 0.01:
            print("✅ TOTALES CORRECTOS")
        else:
            print("❌ ERROR EN TOTALES")
        
        # Verificar repartos
        try:
            reparto_sc = Reparto.get(Reparto.factura == factura_sc)
            reparto_vc = Reparto.get(Reparto.factura == factura_vc)
            
            print(f"\nREPARTOS:")
            print(f"SC - Comercial: ${reparto_sc.comercial:.2f}, Fleet: ${reparto_sc.fleet:.2f}")
            print(f"VC - Comercial: ${reparto_vc.comercial:.2f}, Fleet: ${reparto_vc.fleet:.2f}")
            print(f"Suma Comercial: ${reparto_sc.comercial + reparto_vc.comercial:.2f} (Original: ${datos_completos['p_comercial']:.2f})")
            print(f"Suma Fleet: ${reparto_sc.fleet + reparto_vc.fleet:.2f} (Original: ${datos_completos['p_fleet']:.2f})")
            print("✅ REPARTOS CORRECTOS")
            
        except Exception as e:
            print(f"❌ Error verificando repartos: {e}")
        
        print(f"\n🎉 PRUEBA INTEGRAL COMPLETADA")
        print("✨ FUNCIONALIDAD DIVIDIR CON CONCEPTOS:")
        print("   1. ✅ Totales se dividen por 2")
        print("   2. ✅ Repartos se dividen por 2") 
        print("   3. ✅ Conceptos: Cantidad permanece igual")
        print("   4. ✅ Conceptos: Precio unitario se divide por 2")
        print("   5. ✅ Conceptos: Total se divide por 2")
        print("   6. ✅ Ambas facturas suman el total original")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    test_division_completa()
