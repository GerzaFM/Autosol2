#!/usr/bin/env python3
"""
Test para verificar que la segunda factura dividida mantiene el mismo folio
"""
import sys
import os
sys.path.insert(0, 'src')

from bd.bd_control import DBManager
from bd.models import Factura

print("=== TEST FOLIO IGUAL EN FACTURAS DIVIDIDAS ===")

# Test: Crear dos facturas divididas con el mismo folio pero series diferentes
print("\n1. Creando primera factura (serie normal)...")
data_primera = {
    "serie": "B",
    "folio": "8042",
    "fecha": "2025-08-08",
    "fecha_emision": "2025-08-08",
    "tipo": "VC",
    "nombre_proveedor": "PROVEEDOR DIVIDIDO",
    "rfc_proveedor": "DIV123456789",
    "nombre_receptor": "TCM MATEHUALA",
    "rfc_receptor": "TMM860630PH1",
    "subtotal": "1000.00",
    "iva_trasladado": "160.00",
    "total": "1160.00",
    "conceptos": [],
    "es_segunda_factura_dividida": False  # Primera factura
}

try:
    dbm = DBManager()
    factura_primera = dbm.guardar_formulario(data_primera)
    print(f"✅ Primera factura creada - Serie: {factura_primera.serie}, Folio: {factura_primera.folio}")
    
except Exception as e:
    print(f"❌ Error en primera factura: {e}")
    exit(1)

print("\n2. Creando segunda factura dividida (misma folio, serie con DIV-)...")
data_segunda = {
    "serie": "B",  # La misma serie original
    "folio": "8042",  # EL MISMO FOLIO que la primera
    "fecha": "2025-08-08",
    "fecha_emision": "2025-08-08",
    "tipo": "VC",
    "nombre_proveedor": "PROVEEDOR DIVIDIDO",
    "rfc_proveedor": "DIV123456789",
    "nombre_receptor": "TCM MATEHUALA",
    "rfc_receptor": "TMM860630PH1",
    "subtotal": "500.00",  # Mitad del monto
    "iva_trasladado": "80.00",
    "total": "580.00",
    "conceptos": [],
    "es_segunda_factura_dividida": True  # Segunda factura dividida
}

try:
    dbm = DBManager()
    factura_segunda = dbm.guardar_formulario(data_segunda)
    print(f"✅ Segunda factura creada - Serie: {factura_segunda.serie}, Folio: {factura_segunda.folio}")
    
    # Verificaciones
    print(f"\n=== VERIFICACIONES ===")
    print(f"Primera factura:  Serie: {factura_primera.serie}, Folio: {factura_primera.folio}")
    print(f"Segunda factura:  Serie: {factura_segunda.serie}, Folio: {factura_segunda.folio}")
    
    # Verificar que tienen el mismo folio
    if factura_primera.folio == factura_segunda.folio:
        print("✅ CORRECTO: Ambas facturas tienen el mismo folio")
    else:
        print(f"❌ ERROR: Folios diferentes - Primera: {factura_primera.folio}, Segunda: {factura_segunda.folio}")
    
    # Verificar que las series son diferentes
    if factura_primera.serie != factura_segunda.serie:
        print("✅ CORRECTO: Las series son diferentes")
        if factura_segunda.serie == f"DIV-{factura_primera.serie}":
            print("✅ CORRECTO: Segunda serie tiene prefijo DIV-")
        else:
            print(f"❌ ERROR: Prefijo DIV- incorrecto")
    else:
        print(f"❌ ERROR: Ambas facturas tienen la misma serie")
    
    # Limpiar
    factura_primera.delete_instance()
    factura_segunda.delete_instance()
    print("\n🧹 Facturas de test eliminadas")
    
except Exception as e:
    print(f"❌ Error en segunda factura: {e}")
    # Limpiar primera factura si hubo error
    try:
        factura_primera.delete_instance()
        print("🧹 Primera factura eliminada")
    except:
        pass

print("\n=== FIN DEL TEST ===")
