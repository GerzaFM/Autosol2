#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de serie DIV- en segunda factura
"""
import sys
import os
sys.path.insert(0, 'src')

from bd.bd_control import DBManager
from bd.models import Factura

print("=== TEST SERIE DIV- PARA SEGUNDA FACTURA ===")

# Test 1: Factura normal (sin división)
print("\n1. Probando factura normal (sin división)...")
data_normal = {
    "serie": "B",
    "folio": "123",
    "fecha": "2025-08-08",
    "fecha_emision": "2025-08-08",
    "tipo": "VC",
    "nombre_proveedor": "PROVEEDOR TEST",
    "rfc_proveedor": "TEST123456789",
    "nombre_receptor": "TCM MATEHUALA",
    "rfc_receptor": "TMM860630PH1",
    "subtotal": "1000.00",
    "iva_trasladado": "160.00",
    "total": "1160.00",
    "conceptos": [],
    "es_segunda_factura_dividida": False  # No es segunda factura
}

try:
    dbm = DBManager()
    factura_normal = dbm.guardar_formulario(data_normal)
    print(f"✅ Factura normal creada - Serie: {factura_normal.serie} (esperado: B)")
    
    # Limpiar para el siguiente test
    factura_normal.delete_instance()
    print("🧹 Factura normal eliminada")
    
except Exception as e:
    print(f"❌ Error en factura normal: {e}")

# Test 2: Segunda factura dividida
print("\n2. Probando segunda factura dividida...")
data_dividida = {
    "serie": "B",
    "folio": "124",
    "fecha": "2025-08-08",
    "fecha_emision": "2025-08-08",
    "tipo": "VC",
    "nombre_proveedor": "PROVEEDOR TEST 2",
    "rfc_proveedor": "TEST123456780",
    "nombre_receptor": "TCM MATEHUALA",
    "rfc_receptor": "TMM860630PH1",
    "subtotal": "500.00",
    "iva_trasladado": "80.00",
    "total": "580.00",
    "conceptos": [],
    "es_segunda_factura_dividida": True  # ES segunda factura dividida
}

try:
    dbm = DBManager()
    factura_dividida = dbm.guardar_formulario(data_dividida)
    print(f"✅ Segunda factura dividida creada - Serie: {factura_dividida.serie} (esperado: DIV-B)")
    
    # Verificar que la serie sea correcta
    if factura_dividida.serie == "DIV-B":
        print("🎉 ¡PREFIJO DIV- AGREGADO CORRECTAMENTE!")
    else:
        print(f"❌ Prefijo incorrecto. Esperado: DIV-B, Obtenido: {factura_dividida.serie}")
    
    # Limpiar
    factura_dividida.delete_instance()
    print("🧹 Factura dividida eliminada")
    
except Exception as e:
    print(f"❌ Error en factura dividida: {e}")

print("\n=== FIN DEL TEST ===")
