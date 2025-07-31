"""
Script para verificar el estado de las facturas divididas en la base de datos
"""
import sys
import os

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from bd.models import db, Factura, Proveedor, Concepto, Reparto
from bd.bd_control import DBManager
import datetime

def verificar_facturas_divididas():
    """Verifica las últimas facturas divididas en la base de datos"""
    print("🔍 VERIFICACIÓN DE FACTURAS DIVIDIDAS")
    print("=" * 50)
    
    try:
        # Inicializar conexión a BD
        db_manager = DBManager()
        
        # Obtener las últimas 10 facturas ordenadas por folio_interno
        facturas_recientes = (
            Factura
            .select()
            .order_by(Factura.folio_interno.desc())
            .limit(10)
        )
        
        print("📋 ÚLTIMAS 10 FACTURAS EN LA BASE DE DATOS:")
        print("-" * 80)
        print(f"{'ID':<4} {'Serie-Folio':<12} {'Tipo':<25} {'Total':<12} {'Fecha':<12}")
        print("-" * 80)
        
        for factura in facturas_recientes:
            tipo_corto = factura.tipo[:22] + "..." if len(factura.tipo) > 25 else factura.tipo
            print(f"{factura.folio_interno:<4} {factura.serie}-{factura.folio:<8} {tipo_corto:<25} ${float(factura.total):<11.2f} {factura.fecha}")
        
        # Buscar pares de facturas divididas (mismo proveedor, fechas similares, totales iguales)
        print(f"\n🔍 BUSCANDO FACTURAS DIVIDIDAS (PARES CON TOTALES IGUALES):")
        print("-" * 60)
        
        facturas_por_proveedor = {}
        
        for factura in facturas_recientes:
            proveedor_id = factura.proveedor.id
            if proveedor_id not in facturas_por_proveedor:
                facturas_por_proveedor[proveedor_id] = []
            facturas_por_proveedor[proveedor_id].append(factura)
        
        encontradas = False
        for proveedor_id, facturas in facturas_por_proveedor.items():
            if len(facturas) >= 2:
                # Buscar pares con el mismo total
                for i, factura1 in enumerate(facturas):
                    for j, factura2 in enumerate(facturas[i+1:], i+1):
                        if (abs(float(factura1.total) - float(factura2.total)) < 0.01 and
                            factura1.fecha == factura2.fecha):
                            
                            encontradas = True
                            print(f"\n✅ PAR DIVIDIDO ENCONTRADO:")
                            print(f"   Proveedor: {factura1.proveedor.nombre}")
                            print(f"   Factura 1: ID={factura1.folio_interno}, Tipo='{factura1.tipo[:30]}', Total=${float(factura1.total):.2f}")
                            print(f"   Factura 2: ID={factura2.folio_interno}, Tipo='{factura2.tipo[:30]}', Total=${float(factura2.total):.2f}")
                            print(f"   Suma total: ${float(factura1.total) + float(factura2.total):.2f}")
                            
                            # Verificar repartos
                            reparto1 = Reparto.get_or_none(Reparto.factura == factura1)
                            reparto2 = Reparto.get_or_none(Reparto.factura == factura2)
                            
                            if reparto1 and reparto2:
                                print(f"   📊 Repartos: Ambas facturas tienen reparto asignado ✅")
                            elif reparto1 or reparto2:
                                print(f"   ⚠️ Repartos: Solo una factura tiene reparto")
                            else:
                                print(f"   ❌ Repartos: Ninguna factura tiene reparto")
        
        if not encontradas:
            print("ℹ️ No se encontraron pares de facturas divididas en las últimas 10 facturas")
        
        # Estadísticas por tipo
        print(f"\n📊 ESTADÍSTICAS POR TIPO DE FACTURA:")
        print("-" * 40)
        
        tipos_count = {}
        total_por_tipo = {}
        
        for factura in facturas_recientes:
            tipo = factura.tipo
            if tipo not in tipos_count:
                tipos_count[tipo] = 0
                total_por_tipo[tipo] = 0
            tipos_count[tipo] += 1
            total_por_tipo[tipo] += float(factura.total)
        
        for tipo, count in tipos_count.items():
            promedio = total_por_tipo[tipo] / count
            print(f"{tipo[:35]:<35}: {count} facturas, Total: ${total_por_tipo[tipo]:.2f}, Promedio: ${promedio:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en verificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.cerrar()

def buscar_facturas_por_folio_interno(folio_interno):
    """Busca una factura específica por folio_interno"""
    print(f"\n🔍 BUSCANDO FACTURA CON FOLIO_INTERNO: {folio_interno}")
    print("=" * 50)
    
    try:
        db_manager = DBManager()
        
        factura = Factura.get_or_none(Factura.folio_interno == folio_interno)
        
        if factura:
            print(f"✅ FACTURA ENCONTRADA:")
            print(f"   Folio interno: {factura.folio_interno}")
            print(f"   Serie-Folio: {factura.serie}-{factura.folio}")
            print(f"   Tipo: {factura.tipo}")
            print(f"   Proveedor: {factura.proveedor.nombre}")
            print(f"   RFC: {factura.rfc_emisor}")
            print(f"   Fecha: {factura.fecha}")
            print(f"   Subtotal: ${float(factura.subtotal):.2f}")
            print(f"   IVA: ${float(factura.iva_trasladado or 0):.2f}")
            print(f"   Retención: ${float(factura.ret_iva or 0):.2f}")
            print(f"   Total: ${float(factura.total):.2f}")
            
            # Buscar conceptos
            conceptos = Concepto.select().where(Concepto.factura == factura)
            if conceptos:
                print(f"\n   📋 CONCEPTOS ({len(conceptos)}):")
                for concepto in conceptos:
                    print(f"      - {concepto.descripcion}: {concepto.cantidad} x ${float(concepto.precio_unitario):.2f} = ${float(concepto.total):.2f}")
            
            # Buscar reparto
            reparto = Reparto.get_or_none(Reparto.factura == factura)
            if reparto:
                print(f"\n   💰 REPARTO:")
                print(f"      Comercial: ${float(reparto.comercial or 0):.2f}")
                print(f"      Fleet: ${float(reparto.fleet or 0):.2f}")
                print(f"      Seminuevos: ${float(reparto.seminuevos or 0):.2f}")
                print(f"      Refacciones: ${float(reparto.refacciones or 0):.2f}")
                print(f"      Servicio: ${float(reparto.servicio or 0):.2f}")
                print(f"      HyP: ${float(reparto.hyp or 0):.2f}")
                print(f"      Administración: ${float(reparto.administracion or 0):.2f}")
            
            return factura
        else:
            print(f"❌ No se encontró factura con folio_interno: {folio_interno}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR en búsqueda: {e}")
        return None
    
    finally:
        if 'db_manager' in locals():
            db_manager.cerrar()

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DE FACTURAS DIVIDIDAS")
    print("=" * 60)
    
    # Verificar facturas divididas
    verificar_facturas_divididas()
    
    # Si hay argumentos, buscar factura específica
    if len(sys.argv) > 1:
        try:
            folio_interno = int(sys.argv[1])
            buscar_facturas_por_folio_interno(folio_interno)
        except ValueError:
            print(f"\n❌ ERROR: '{sys.argv[1]}' no es un número válido para folio_interno")
    
    print(f"\n✨ DIAGNÓSTICO COMPLETADO")
    print("💡 Para buscar una factura específica, use: python diagnostico_facturas.py [folio_interno]")
