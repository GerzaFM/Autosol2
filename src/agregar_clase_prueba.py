#!/usr/bin/env python3
"""
Script para agregar valores de prueba al campo clase
"""
import sys
import os
from bd.models import Factura, db

def agregar_clase_prueba():
    """Agrega valores de prueba al campo clase."""
    try:
        # Conectar a la base de datos
        db.init('../facturas.db')
        
        print("Agregando valores de prueba al campo clase...")
        
        # Actualizar primera factura
        f1 = Factura.get(Factura.folio_interno == 1)
        f1.clase = 'Construcción'
        f1.save()
        print(f"  Factura {f1.folio_interno}: clase = 'Construcción'")
        
        # Actualizar segunda factura
        f2 = Factura.get(Factura.folio_interno == 3)
        f2.clase = 'Materiales'
        f2.save()
        print(f"  Factura {f2.folio_interno}: clase = 'Materiales'")
        
        print("Valores de prueba agregados correctamente")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    agregar_clase_prueba()
