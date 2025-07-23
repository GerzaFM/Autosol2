#!/usr/bin/env python3
"""
Script para verificar el estado del campo clase
"""
import sys
import os
from bd.models import Factura, db

def verificar_clase():
    """Verifica el contenido del campo clase en las facturas."""
    try:
        # Conectar a la base de datos
        db.init('../facturas.db')
        
        print("Estado actual del campo clase:")
        facturas = list(Factura.select())
        
        for f in facturas:
            clase_str = f.clase if f.clase else "(vacío)"
            print(f"  ID: {f.folio_interno}, Serie-Folio: {f.serie}-{f.folio}, Clase: \"{clase_str}\"")
        
        print(f"\nTotal de facturas: {len(facturas)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_clase()
