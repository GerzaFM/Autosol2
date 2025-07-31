"""
Script de diagnóstico específico para el problema de UNIQUE constraint
"""
import sys
import os
import traceback

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from bd.models import db, Factura, Proveedor, Concepto, Reparto
from bd.bd_control import DBManager
import sqlite3

def diagnóstico_detallado():
    print("🔍 DIAGNÓSTICO DETALLADO DEL PROBLEMA UNIQUE CONSTRAINT")
    print("=" * 60)
    
    try:
        # Paso 1: Verificar estado actual de la base de datos
        print("PASO 1: Estado actual de la base de datos")
        print("-" * 40)
        
        db_manager = DBManager()
        
        # Verificar secuencia de folio_interno
        última_factura = Factura.select().order_by(Factura.folio_interno.desc()).limit(1)
        if última_factura:
            último_folio = última_factura[0].folio_interno
            print(f"✅ Último folio_interno: {último_folio}")
        else:
            último_folio = 0
            print("⚠️ No hay facturas en la base de datos")
        
        # Verificar secuencia de reparto
        último_reparto = Reparto.select().order_by(Reparto.id.desc()).limit(1)
        if último_reparto:
            último_reparto_id = último_reparto[0].id
            último_reparto_factura = último_reparto[0].factura.folio_interno
            print(f"✅ Último reparto ID: {último_reparto_id}, Factura: {último_reparto_factura}")
        else:
            print("⚠️ No hay repartos en la base de datos")
        
        db_manager.cerrar()
        
        # Paso 2: Crear un proveedor de prueba limpio
        print(f"\nPASO 2: Creando proveedor de prueba")
        print("-" * 40)
        
        db_manager = DBManager()
        
        # Limpiar proveedor existente
        with db.atomic():
            Proveedor.delete().where(Proveedor.rfc == "DIAG123456789").execute()
        
        # Crear proveedor
        proveedor, created = Proveedor.get_or_create(
            rfc="DIAG123456789",
            defaults={
                "nombre": "DIAGNÓSTICO SA DE CV",
                "telefono": "1234567890",
                "email": "diag@test.com",
                "nombre_contacto": "Juan Test"
            }
        )
        
        print(f"✅ Proveedor {'creado' if created else 'reutilizado'}: {proveedor.nombre} (ID: {proveedor.id})")
        
        db_manager.cerrar()
        
        # Paso 3: Crear factura manualmente paso a paso
        print(f"\nPASO 3: Creando factura paso a paso")
        print("-" * 40)
        
        db_manager = DBManager()
        
        try:
            with db.atomic():
                # Crear factura
                print("📝 Creando factura...")
                nueva_factura = Factura.create(
                    serie="DIAG",
                    folio=99999,
                    fecha="2025-07-30",
                    fecha_emision="2025-07-30",
                    tipo="DIAGNÓSTICO",
                    nombre_emisor="DIAGNÓSTICO SA DE CV",
                    rfc_emisor="DIAG123456789",
                    nombre_receptor="TCM MATEHUALA",
                    rfc_receptor="TMM860630PH1",
                    subtotal=100.00,
                    iva_trasladado=16.00,
                    ret_iva=1.00,
                    ret_isr=0.00,
                    total=115.00,
                    comentario="Factura de diagnóstico",
                    proveedor=proveedor
                )
                
                print(f"✅ Factura creada con folio_interno: {nueva_factura.folio_interno}")
                
                # Crear concepto
                print("📝 Creando concepto...")
                Concepto.create(
                    descripcion="Servicio de diagnóstico",
                    cantidad=1,
                    precio_unitario=100.00,
                    total=100.00,
                    factura=nueva_factura
                )
                print("✅ Concepto creado")
                
                # Crear reparto
                print("📝 Creando reparto...")
                nuevo_reparto = Reparto.create(
                    comercial=50.00,
                    fleet=50.00,
                    seminuevos=0.00,
                    refacciones=15.00,
                    servicio=0.00,
                    hyp=0.00,
                    administracion=0.00,
                    factura=nueva_factura
                )
                print(f"✅ Reparto creado con ID: {nuevo_reparto.id}, Factura: {nuevo_reparto.factura.folio_interno}")
                
                print(f"\n🎉 TODO COMPLETADO EXITOSAMENTE")
                print(f"   Factura: {nueva_factura.folio_interno}")
                print(f"   Reparto: {nuevo_reparto.id}")
                
        except Exception as e:
            print(f"❌ ERROR en creación manual: {e}")
            print("Traceback:")
            traceback.print_exc()
            
            # Diagnóstico adicional: ver si existe un reparto con la misma factura_id
            try:
                reparto_existente = Reparto.get_or_none(Reparto.factura == nueva_factura.folio_interno)
                if reparto_existente:
                    print(f"🔍 DIAGNÓSTICO: Ya existe reparto para factura {nueva_factura.folio_interno}")
                    print(f"    Reparto ID: {reparto_existente.id}")
                else:
                    print(f"🔍 DIAGNÓSTICO: NO existe reparto previo para factura {nueva_factura.folio_interno}")
            except Exception as diag_error:
                print(f"🔍 DIAGNÓSTICO: Error en verificación: {diag_error}")
        
        finally:
            db_manager.cerrar()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnóstico_detallado()
