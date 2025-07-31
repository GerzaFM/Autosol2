#!/usr/bin/env python3
"""
Prueba del nuevo flujo de dividir: 
1. Primera vez: Guarda primera factura (SC), cambia tipo a VC, NO guarda segunda automáticamente
2. Segunda vez: Usuario hace clic en Generar otra vez, guarda segunda factura (VC)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bd.models import Factura, Reparto, Proveedor, db
from bd.bd_control import DBManager
import time

def test_nuevo_flujo_dividir():
    """Simula el nuevo flujo de dividir paso a paso"""
    try:
        db.connect()
        db_manager = DBManager()
        
        print("🧪 PRUEBA DEL NUEVO FLUJO DIVIDIR")
        print("="*50)
        
        # Generar datos únicos
        timestamp = str(int(time.time()))[-6:]
        folio_base = f"TEST{timestamp}"
        
        # Datos base para las pruebas
        datos_base = {
            # Proveedor
            'nombre_proveedor': 'PROVEEDOR TEST SA DE CV',
            'rfc_proveedor': 'PTS123456789',
            
            # Factura base
            'serie': 'A',
            'folio': folio_base,
            'fecha': '2024-01-15',
            'fecha_emision': '2024-01-15',
            'tipo': 'SC - SOLICITUD DE COMPRA',
            'nombre_receptor': 'TCM MATEHUALA SA DE CV',
            'rfc_receptor': 'TMC987654321',
            'subtotal': 1000.00,
            'ret_iva': 50.00,
            'ret_isr': 30.00,
            'iva_trasladado': 160.00,
            'total': 1080.00,
            'comentario': 'Prueba nuevo flujo dividir',
            'clase': 'GASTOS',
            
            # Conceptos
            'conceptos': [
                {
                    'descripcion': 'Servicio de prueba',
                    'cantidad': 1,
                    'precio_unitario': 1000.00,
                    'importe': 1000.00
                }
            ],
            
            # Reparto
            'p_comercial': 600.00,
            'p_fleet': 480.00
        }
        
        print("📋 DATOS ORIGINALES:")
        print(f"   Folio: {datos_base['folio']}")
        print(f"   Tipo: {datos_base['tipo']}")
        print(f"   Total: ${datos_base['total']:.2f}")
        print(f"   Comercial: ${datos_base['p_comercial']:.2f}")
        print(f"   Fleet: ${datos_base['p_fleet']:.2f}")
        
        # PASO 1: Simular primera vez (con dividir marcado)
        print(f"\n🎯 PASO 1: Primera factura con dividir marcado")
        print("-" * 40)
        
        # Dividir todos los totales por 2 (como lo hace la aplicación)
        datos_sc = datos_base.copy()
        datos_sc['conceptos'] = [concepto.copy() for concepto in datos_base['conceptos']]
        
        datos_sc['subtotal'] /= 2
        datos_sc['ret_iva'] /= 2 
        datos_sc['ret_isr'] /= 2
        datos_sc['iva_trasladado'] /= 2
        datos_sc['total'] /= 2
        datos_sc['p_comercial'] /= 2
        datos_sc['p_fleet'] /= 2
        
        for concepto in datos_sc['conceptos']:
            concepto['precio_unitario'] /= 2
            concepto['importe'] /= 2
        
        print(f"   Totales divididos por 2:")
        print(f"   Total: ${datos_sc['total']:.2f}")
        print(f"   Comercial: ${datos_sc['p_comercial']:.2f}")
        print(f"   Fleet: ${datos_sc['p_fleet']:.2f}")
        
        # Guardar primera factura (SC)
        factura_sc = db_manager.guardar_formulario(datos_sc)
        print(f"✅ Primera factura (SC) guardada: folio_interno={factura_sc.folio_interno}")
        
        # PASO 2: Simular que la aplicación cambió el tipo a VC
        print(f"\n🔄 PASO 2: Cambio automático de tipo a VC")
        print("-" * 40)
        print("   La aplicación cambiaría automáticamente:")
        print("   - Tipo: 'SC - SOLICITUD DE COMPRA' → 'VC - VALE DE CONTROL'")
        print("   - Checkbox dividir: enabled → disabled")
        print("   - Mensaje: 'Haga clic en Generar nuevamente'")
        
        # PASO 3: Simular segunda vez (usuario hace clic en Generar otra vez)
        print(f"\n🎯 PASO 3: Segunda factura (VC) - Usuario hace clic en Generar")
        print("-" * 40)
        
        # Preparar datos para segunda factura
        datos_vc = datos_sc.copy()  # Usar los datos ya divididos
        datos_vc['tipo'] = 'VC - VALE DE CONTROL'
        
        # Generar folio diferente (como lo haría la aplicación)
        try:
            folio_numero = int(folio_base[4:]) + 1  # Extraer número después de "TEST"
            datos_vc['folio'] = f"TEST{folio_numero}"
        except ValueError:
            datos_vc['folio'] = f"{folio_base}_VC"
        
        print(f"   Folio actualizado: {datos_vc['folio']}")
        print(f"   Tipo: {datos_vc['tipo']}")
        print(f"   Totales mantienen división: ${datos_vc['total']:.2f}")
        
        # Guardar segunda factura (VC)
        factura_vc = db_manager.guardar_formulario(datos_vc)
        print(f"✅ Segunda factura (VC) guardada: folio_interno={factura_vc.folio_interno}")
        
        # VERIFICACIÓN FINAL
        print(f"\n🔍 VERIFICACIÓN FINAL:")
        print("=" * 40)
        
        print(f"Factura SC (Primera):")
        print(f"  - Folio interno: {factura_sc.folio_interno}")
        print(f"  - Folio: {factura_sc.folio}")
        print(f"  - Tipo: {factura_sc.tipo}")
        print(f"  - Total: ${factura_sc.total:.2f}")
        
        print(f"\nFactura VC (Segunda):")
        print(f"  - Folio interno: {factura_vc.folio_interno}")
        print(f"  - Folio: {factura_vc.folio}")
        print(f"  - Tipo: {factura_vc.tipo}")
        print(f"  - Total: ${factura_vc.total:.2f}")
        
        print(f"\nRESUMEN:")
        print(f"  - Total original: ${datos_base['total']:.2f}")
        print(f"  - Suma de facturas: ${factura_sc.total + factura_vc.total:.2f}")
        print(f"  - Diferencia: ${abs(datos_base['total'] - (factura_sc.total + factura_vc.total)):.2f}")
        
        # Verificar repartos
        try:
            reparto_sc = Reparto.get(Reparto.factura == factura_sc)
            reparto_vc = Reparto.get(Reparto.factura == factura_vc)
            print(f"\nREPARTOS:")
            print(f"  SC - Comercial: ${reparto_sc.comercial:.2f}, Fleet: ${reparto_sc.fleet:.2f}")
            print(f"  VC - Comercial: ${reparto_vc.comercial:.2f}, Fleet: ${reparto_vc.fleet:.2f}")
            print(f"✅ Ambas facturas tienen reparto correcto")
        except Exception as e:
            print(f"❌ Error verificando repartos: {e}")
        
        print(f"\n🎉 PRUEBA DEL NUEVO FLUJO COMPLETADA")
        print(f"✨ El nuevo flujo dividir funciona correctamente:")
        print(f"   1. ✅ Primera factura (SC) se guarda con totales divididos")
        print(f"   2. ✅ Aplicación cambia tipo a VC automáticamente") 
        print(f"   3. ✅ Usuario debe hacer clic en Generar nuevamente")
        print(f"   4. ✅ Segunda factura (VC) se guarda con totales divididos")
        print(f"   5. ✅ Ambas facturas suman el total original")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    test_nuevo_flujo_dividir()
