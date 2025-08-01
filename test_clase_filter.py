#!/usr/bin/env python3
"""
Script de prueba para verificar el filtro de clase
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.bd.models import Factura

def test_clase_filter():
    """Prueba el filtro de clase"""
    print("=== PRUEBA DEL FILTRO DE CLASE ===\n")
    
    try:
        # Obtener valores únicos de clase
        print("1. Obteniendo clases únicas de la base de datos...")
        clases_query = (Factura
                      .select(Factura.clase)
                      .where(Factura.clase.is_null(False) & (Factura.clase != ''))
                      .distinct()
                      .order_by(Factura.clase))
        
        clases_data = []
        for factura in clases_query:
            if factura.clase and factura.clase.strip():
                clases_data.append(factura.clase.strip())
        
        clases_data = sorted(list(set(clases_data)))
        
        print(f"   Clases encontradas: {len(clases_data)}")
        for i, clase in enumerate(clases_data, 1):
            print(f"   {i}. {clase}")
        
        print("\n2. Contando facturas por clase...")
        for clase in clases_data:
            count = Factura.select().where(Factura.clase == clase).count()
            print(f"   {clase}: {count} facturas")
        
        print("\n3. Contando facturas sin clase...")
        sin_clase = Factura.select().where(
            (Factura.clase.is_null(True)) | (Factura.clase == '')
        ).count()
        print(f"   Sin clase: {sin_clase} facturas")
        
        total_facturas = Factura.select().count()
        print(f"\n   Total de facturas: {total_facturas}")
        
        print("\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clase_filter()
