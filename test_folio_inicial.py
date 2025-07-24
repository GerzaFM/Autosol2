#!/usr/bin/env python3
"""
Script para probar el diálogo de folio manual con valor inicial
"""

import sys
import os

# Agregar rutas para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from src.bd.bd_control import DBManager
    from src.bd.models import Proveedor, Factura, Reparto
    from src.solicitudapp.ctrl_xml import XMLFactura
    print("✅ Importación exitosa desde src/")
except ImportError:
    try:
        from bd.bd_control import DBManager
        from bd.models import Proveedor, Factura, Reparto
        from solicitudapp.ctrl_xml import XMLFactura
        print("✅ Importación exitosa desde bd/ y solicitudapp/")
    except ImportError as e:
        print(f"❌ Error en importaciones: {e}")
        sys.exit(1)

def crear_factura_prueba():
    """Crea una factura de prueba en la base de datos"""
    print("\n📝 Creando factura de prueba...")
    
    # Inicializar base de datos
    db_manager = DBManager()
    
    # Crear proveedor de prueba
    proveedor = Proveedor.get_or_create(
        rfc="AAA010101AAA",
        defaults={
            'nombre': "Proveedor de Prueba S.A. de C.V.",
            'nombre_corto': "PROVEEDOR PRUEBA"
        }
    )[0]
    
    # Crear factura de prueba
    factura = Factura.create(
        proveedor=proveedor,
        serie="A",
        folio="8954",
        folio_interno="INT-2024-001",
        monto_total=1500.00,
        fecha="2024-07-18",
        metodo_pago="PUE",
        forma_pago="03",
        moneda="MXN",
        tipo_cambio=1.0,
        uso_cfdi="G03",
        lugar_expedicion="78000"
    )
    
    print(f"✅ Factura creada:")
    print(f"   - RFC: {proveedor.rfc}")
    print(f"   - Serie: {factura.serie}")
    print(f"   - Folio: {factura.folio}")
    print(f"   - Folio interno: {factura.folio_interno}")
    print(f"   - Monto: ${factura.monto_total}")
    
    return factura

def main():
    print("🧪 Test del diálogo de folio inicial")
    print("=" * 50)
    
    # Crear factura de prueba
    factura_prueba = crear_factura_prueba()
    
    print(f"\n✅ Factura de prueba lista con folio interno: {factura_prueba.folio_interno}")
    print("\n📋 Información para prueba manual:")
    print(f"   - Archivo XML de prueba: 8954.xml")
    print(f"   - Esta factura ya existe en BD con folio interno: {factura_prueba.folio_interno}")
    print(f"   - Al cargar el XML, debería mostrar este folio como valor inicial")
    
    print("\n🔍 Verificando datos en base de datos...")
    
    # Verificar que la factura existe
    facturas = Factura.select()
    print(f"   - Total de facturas en BD: {facturas.count()}")
    
    for f in facturas:
        print(f"   - Factura: Serie {f.serie}, Folio {f.folio}, Folio interno: {f.folio_interno}")

if __name__ == "__main__":
    main()
