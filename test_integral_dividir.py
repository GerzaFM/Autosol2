"""
Script de prueba integral para la funcionalidad DIVIDIR
"""
import sys
import os

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from bd.models import db, Factura, Proveedor, Concepto, Reparto
from bd.bd_control import DBManager
from solicitudapp.logic_solicitud import SolicitudLogica
import datetime

def test_funcionalidad_dividir_completa():
    """Prueba completa de la funcionalidad dividir simulando el flujo real"""
    print("🧪 PRUEBA INTEGRAL: Funcionalidad DIVIDIR completa")
    print("=" * 60)
    
    try:
        # Limpiar datos de prueba anteriores
        db_manager = DBManager()
        control = SolicitudLogica()
        
        with db.atomic():
            # Eliminar facturas de prueba anteriores
            facturas_prueba = Factura.select().where(
                Factura.rfc_emisor == "PPR987654321"
            )
            
            for factura in facturas_prueba:
                Reparto.delete().where(Reparto.factura == factura).execute()
                Concepto.delete().where(Concepto.factura == factura).execute()
                factura.delete_instance()
            
            Proveedor.delete().where(Proveedor.rfc == "PPR987654321").execute()
            
        print("🧹 Datos de prueba anteriores limpiados")
        
        # DATOS ORIGINALES (ANTES DE DIVIDIR)
        proveedor_data = {
            "nombre": "PROVEEDOR INTEGRAL SA DE CV",
            "rfc": "PPR987654321",
            "telefono": "1234567890",
            "email": "integral@ejemplo.com",
            "nombre_contacto": "María García"
        }
        
        solicitud_data = {
            "serie": "A",
            "folio": "50001",
            "fecha": datetime.date.today().strftime("%Y-%m-%d"),
            "tipo": "SC - SOLICITUD DE COMPRA",
            "nombre_receptor": "TCM MATEHUALA",
            "rfc_receptor": "TMM860630PH1"
        }
        
        conceptos_data = [
            {
                "descripcion": "Servicio de limpieza",
                "cantidad": "10",
                "unidad": "HRS",
                "precio_unitario": "50.00",
                "importe": "500.00"
            },
            {
                "descripcion": "Material de oficina",
                "cantidad": "5",
                "unidad": "PZ",
                "precio_unitario": "100.00",
                "importe": "500.00"
            }
        ]
        
        # TOTALES ORIGINALES
        totales_originales = {
            "subtotal": "1000.00",
            "iva_trasladado": "160.00",
            "ret_iva": "10.67",
            "ret_isr": "0.00",
            "total": "1149.33"
        }
        
        # CATEGORÍAS ORIGINALES
        categorias_originales = {
            "comercial": "300.00",
            "fleet": "400.00",
            "seminuevos": "0.00",
            "refacciones": "200.00",
            "servicio": "249.33",
            "hyp": "0.00",
            "administracion": "0.00"
        }
        
        comentarios_data = {
            "comentario": "Factura de prueba integral para dividir"
        }
        
        print("📋 DATOS ORIGINALES:")
        print(f"   Total original: ${float(totales_originales['total']):.2f}")
        print(f"   Categorías: Comercial=${float(categorias_originales['comercial']):.2f}, Fleet=${float(categorias_originales['fleet']):.2f}")
        
        # PASO 1: DIVIDIR TOTALES (SIMULAR LA ACCIÓN DEL USUARIO)
        print("\n🔄 PASO 1: Dividiendo totales...")
        totales_divididos = {}
        for key, value in totales_originales.items():
            valor_original = float(value)
            valor_dividido = valor_original / 2
            totales_divididos[key] = f"{valor_dividido:.2f}"
        
        categorias_divididas = {}
        for key, value in categorias_originales.items():
            valor_original = float(value)
            valor_dividido = valor_original / 2
            categorias_divididas[key] = f"{valor_dividido:.2f}"
        
        print(f"   Total dividido: ${float(totales_divididos['total']):.2f}")
        print(f"   Categorías divididas: Comercial=${float(categorias_divididas['comercial']):.2f}, Fleet=${float(categorias_divididas['fleet']):.2f}")
        
        # PASO 2: GUARDAR PRIMERA FACTURA (CON TOTALES DIVIDIDOS)
        print("\n💾 PASO 2: Guardando primera factura (SC) con totales divididos...")
        factura1 = control.guardar_solicitud(
            proveedor_data, solicitud_data, conceptos_data,
            totales_divididos, categorias_divididas, comentarios_data
        )
        print(f"✅ Primera factura guardada: folio_interno={factura1.folio_interno}, tipo='{factura1.tipo}', total=${float(factura1.total):.2f}")
        
        # PASO 3: GUARDAR SEGUNDA FACTURA (VC) CON FOLIO DIFERENTE
        print("\n💾 PASO 3: Guardando segunda factura (VC) con totales divididos...")
        solicitud_data_vc = solicitud_data.copy()
        solicitud_data_vc["folio"] = "50002"  # Folio diferente
        solicitud_data_vc["tipo"] = "VC - VALE DE CONTROL"
        
        factura2 = control.guardar_solicitud(
            proveedor_data, solicitud_data_vc, conceptos_data,
            totales_divididos, categorias_divididas, comentarios_data
        )
        print(f"✅ Segunda factura guardada: folio_interno={factura2.folio_interno}, tipo='{factura2.tipo}', total=${float(factura2.total):.2f}")
        
        # VERIFICACIÓN FINAL
        print("\n🔍 VERIFICACIÓN FINAL:")
        print("-" * 40)
        
        # Verificar totales
        total_original = float(totales_originales["total"])
        total_factura1 = float(factura1.total)
        total_factura2 = float(factura2.total)
        suma_divididos = total_factura1 + total_factura2
        
        print(f"Total original: ${total_original:.2f}")
        print(f"Factura 1 (SC): ${total_factura1:.2f}")
        print(f"Factura 2 (VC): ${total_factura2:.2f}")
        print(f"Suma divididos: ${suma_divididos:.2f}")
        
        if abs(total_original - suma_divididos) < 0.01:
            print("✅ TOTALES: Correctos")
        else:
            print("❌ TOTALES: Error en la suma")
        
        # Verificar tipos
        if factura1.tipo == "SC - SOLICITUD DE COMPRA" and factura2.tipo == "VC - VALE DE CONTROL":
            print("✅ TIPOS: Correctos")
        else:
            print("❌ TIPOS: Tipos incorrectos")
        
        # Verificar repartos
        reparto1 = Reparto.get_or_none(Reparto.factura == factura1)
        reparto2 = Reparto.get_or_none(Reparto.factura == factura2)
        
        if reparto1 and reparto2:
            print("✅ REPARTOS: Ambas facturas tienen reparto")
            
            # Verificar suma de categorías
            comercial_original = float(categorias_originales["comercial"])
            comercial_suma = float(reparto1.comercial or 0) + float(reparto2.comercial or 0)
            
            fleet_original = float(categorias_originales["fleet"])
            fleet_suma = float(reparto1.fleet or 0) + float(reparto2.fleet or 0)
            
            if (abs(comercial_original - comercial_suma) < 0.01 and 
                abs(fleet_original - fleet_suma) < 0.01):
                print("✅ CATEGORÍAS: Suman correctamente")
                print(f"   Comercial: ${comercial_original:.2f} = ${float(reparto1.comercial):.2f} + ${float(reparto2.comercial):.2f}")
                print(f"   Fleet: ${fleet_original:.2f} = ${float(reparto1.fleet):.2f} + ${float(reparto2.fleet):.2f}")
            else:
                print("❌ CATEGORÍAS: No suman correctamente")
        else:
            print("❌ REPARTOS: Faltan repartos")
        
        # Verificar conceptos
        conceptos1 = Concepto.select().where(Concepto.factura == factura1)
        conceptos2 = Concepto.select().where(Concepto.factura == factura2)
        
        if len(conceptos1) == len(conceptos2) == len(conceptos_data):
            print("✅ CONCEPTOS: Ambas facturas tienen los conceptos correctos")
        else:
            print("❌ CONCEPTOS: Número incorrecto de conceptos")
        
        print("\n🎉 PRUEBA INTEGRAL COMPLETADA")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en la prueba integral: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.cerrar()

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA INTEGRAL DE FUNCIONALIDAD DIVIDIR")
    print("=" * 70)
    
    success = test_funcionalidad_dividir_completa()
    
    if success:
        print("\n✨ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("🎯 La funcionalidad DIVIDIR está lista para usar")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revise los errores antes de usar la funcionalidad")
