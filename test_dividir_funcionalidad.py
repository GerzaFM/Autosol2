"""
Script para probar la funcionalidad de dividir en solicitud_app_professional
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

def test_guardar_factura_dividida():
    """Prueba el guardado de facturas divididas"""
    print("🧪 PRUEBA: Guardado de facturas divididas")
    print("=" * 50)
    
    try:
        # Inicializar controladores
        db_manager = DBManager()
        control = SolicitudLogica()
        
        # Limpiar datos de prueba anteriores (solo para la prueba)
        with db.atomic():
            # Eliminar facturas de prueba anteriores
            facturas_prueba = Factura.select().where(
                (Factura.folio == 12345) | (Factura.folio == 12346)
            )
            for factura in facturas_prueba:
                # Eliminar repartos asociados
                Reparto.delete().where(Reparto.factura == factura).execute()
                # Eliminar conceptos asociados  
                Concepto.delete().where(Concepto.factura == factura).execute()
                # Eliminar la factura
                factura.delete_instance()
            
            # Eliminar proveedor de prueba anterior
            Proveedor.delete().where(Proveedor.rfc == "PPR123456789").execute()
            
        print("🧹 Datos de prueba anteriores limpiados")
        
        # Datos de prueba para primera factura (original)
        proveedor_data = {
            "nombre": "PROVEEDOR DE PRUEBA SA DE CV",
            "rfc": "PPR123456789",
            "telefono": "1234567890",
            "email": "prueba@ejemplo.com",
            "nombre_contacto": "Juan Pérez"
        }
        
        solicitud_data = {
            "serie": "A",
            "folio": "12345",
            "fecha": datetime.date.today().strftime("%Y-%m-%d"),
            "tipo": "SC - SOLICITUD DE COMPRA",
            "nombre_receptor": "TCM MATEHUALA",
            "rfc_receptor": "TMM860630PH1"
        }
        
        conceptos_data = [
            {
                "descripcion": "Producto de prueba 1",
                "cantidad": "2",
                "unidad": "PZ",
                "precio_unitario": "100.00",
                "importe": "200.00"
            },
            {
                "descripcion": "Producto de prueba 2",
                "cantidad": "1",
                "unidad": "PZ",
                "precio_unitario": "150.00",
                "importe": "150.00"
            }
        ]
        
        totales_data = {
            "subtotal": "350.00",
            "iva_trasladado": "56.00",
            "ret_iva": "5.60",
            "ret_isr": "0",
            "total": "400.40"
        }
        
        categorias_data = {
            "comercial": "100.00",
            "fleet": "200.00",
            "seminuevos": "0",
            "refacciones": "100.40",
            "servicio": "0",
            "hyp": "0",
            "administracion": "0"
        }
        
        comentarios_data = {
            "comentario": "Factura de prueba para dividir"
        }
        
        # Guardar primera factura (original)
        print("📝 Guardando primera factura (original)...")
        factura1 = control.guardar_solicitud(
            proveedor_data, solicitud_data, conceptos_data,
            totales_data, categorias_data, comentarios_data
        )
        print(f"✅ Primera factura guardada con folio_interno: {factura1.folio_interno}")
        
        # Simular división de totales (mitad de cada valor)
        totales_divididos = {
            "subtotal": "175.00",
            "iva_trasladado": "28.00",
            "ret_iva": "2.80",
            "ret_isr": "0",
            "total": "200.20"
        }
        
        categorias_divididas = {
            "comercial": "50.00",
            "fleet": "100.00",
            "seminuevos": "0",
            "refacciones": "50.20",
            "servicio": "0",
            "hyp": "0",
            "administracion": "0"
        }
        
        # Datos para segunda factura (VC) - IMPORTANTE: diferente folio
        solicitud_data_vc = solicitud_data.copy()
        solicitud_data_vc["folio"] = "12346"  # Diferente folio
        solicitud_data_vc["tipo"] = "VC - VALE DE CONTROL"
        
        # Guardar segunda factura (VC)
        print("📝 Guardando segunda factura (VC - dividida)...")
        factura2 = control.guardar_solicitud(
            proveedor_data, solicitud_data_vc, conceptos_data,
            totales_divididos, categorias_divididas, comentarios_data
        )
        print(f"✅ Segunda factura (VC) guardada con folio_interno: {factura2.folio_interno}")
        
        # Verificar que ambas facturas se guardaron correctamente
        print("\n🔍 VERIFICACIÓN:")
        print(f"Factura 1: folio_interno={factura1.folio_interno}, tipo='{factura1.tipo}', total={factura1.total}")
        print(f"Factura 2: folio_interno={factura2.folio_interno}, tipo='{factura2.tipo}', total={factura2.total}")
        
        # Verificar suma de totales divididos
        total_original = float(totales_data["total"])
        total_dividido_1 = float(factura1.total)
        total_dividido_2 = float(factura2.total)
        suma_divididos = total_dividido_1 + total_dividido_2
        
        print(f"\n📊 COMPARACIÓN DE TOTALES:")
        print(f"Total original: ${total_original:.2f}")
        print(f"Total dividido (factura 1): ${total_dividido_1:.2f}")
        print(f"Total dividido (factura 2): ${total_dividido_2:.2f}")
        print(f"Suma de divididos: ${suma_divididos:.2f}")
        
        if abs(total_original - suma_divididos) < 0.01:  # Tolerancia para redondeos
            print("✅ Los totales divididos suman correctamente")
        else:
            print("❌ ERROR: Los totales divididos no suman correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.cerrar()

def test_verificar_modelo_factura():
    """Verifica que el modelo Factura tenga todos los campos necesarios"""
    print("\n🔍 VERIFICACIÓN DEL MODELO FACTURA")
    print("=" * 40)
    
    try:
        # Conectar a la base de datos
        db_manager = DBManager()
        
        # Obtener las columnas de la tabla Factura
        with db.atomic():
            cursor = db.execute_sql("PRAGMA table_info(factura);")
            columns = cursor.fetchall()
        
        print("📋 Columnas de la tabla Factura:")
        for col in columns:
            cid, name, data_type, notnull, default, pk = col
            pk_indicator = " (PK)" if pk else ""
            print(f"  - {name}: {data_type}{pk_indicator}")
        
        # Verificar campos críticos
        column_names = [col[1] for col in columns]
        campos_criticos = ['folio_interno', 'serie', 'folio', 'tipo', 'total']
        
        print(f"\n✅ Verificando campos críticos:")
        for campo in campos_criticos:
            if campo in column_names:
                print(f"  ✅ {campo}: OK")
            else:
                print(f"  ❌ {campo}: FALTANTE")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en verificación del modelo: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.cerrar()

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FUNCIONALIDAD DIVIDIR")
    print("=" * 60)
    
    # Verificar modelo
    test_verificar_modelo_factura()
    
    # Probar funcionalidad
    test_guardar_factura_dividida()
    
    print("\n✅ PRUEBAS COMPLETADAS")
