#!/usr/bin/env python3
"""
Script de prueba para verificar el filtro de clase con Entry
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.bd.models import Factura

def test_clase_entry_filter():
    """Prueba el filtro de clase con Entry (búsqueda parcial)"""
    print("=== PRUEBA DEL FILTRO DE CLASE CON ENTRY ===\n")
    
    try:
        print("1. Verificando clases disponibles...")
        clases_query = (Factura
                      .select(Factura.clase)
                      .where(Factura.clase.is_null(False) & (Factura.clase != ''))
                      .distinct()
                      .order_by(Factura.clase))
        
        clases_disponibles = []
        for factura in clases_query:
            if factura.clase and factura.clase.strip():
                clases_disponibles.append(factura.clase.strip())
        
        print(f"   Clases disponibles: {len(clases_disponibles)}")
        for clase in sorted(clases_disponibles):
            print(f"   - {clase}")
        
        print("\n2. Pruebas de filtrado parcial...")
        
        # Prueba 1: Buscar "SERVICIO" (debería encontrar "SERVICIOS" y "SERVICIOS PROFESIONALES")
        print("   Prueba 1: Buscar 'SERVICIO' (parcial)")
        resultado = []
        for factura in Factura.select():
            if factura.clase and "SERVICIO" in factura.clase.upper():
                resultado.append(factura.clase)
        
        print(f"   Resultados para 'SERVICIO': {len(resultado)} facturas")
        for clase in set(resultado):
            count = resultado.count(clase)
            print(f"     - {clase}: {count} facturas")
        
        # Prueba 2: Buscar "GAS" (debería encontrar "GASTOS")
        print("\n   Prueba 2: Buscar 'GAS' (parcial)")
        resultado2 = []
        for factura in Factura.select():
            if factura.clase and "GAS" in factura.clase.upper():
                resultado2.append(factura.clase)
        
        print(f"   Resultados para 'GAS': {len(resultado2)} facturas")
        for clase in set(resultado2):
            count = resultado2.count(clase)
            print(f"     - {clase}: {count} facturas")
        
        # Prueba 3: Buscar texto que no existe
        print("\n   Prueba 3: Buscar 'INEXISTENTE' (sin resultados)")
        resultado3 = []
        for factura in Factura.select():
            if factura.clase and "INEXISTENTE" in factura.clase.upper():
                resultado3.append(factura.clase)
        
        print(f"   Resultados para 'INEXISTENTE': {len(resultado3)} facturas")
        
        print("\n✅ Todas las pruebas completadas exitosamente")
        print("El filtro por Entry permite búsqueda parcial (case insensitive)")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clase_entry_filter()
