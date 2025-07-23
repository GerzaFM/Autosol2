#!/usr/bin/env python3
"""
Script de prueba para verificar que el campo 'clase' funciona correctamente.
"""
import sys
import os
from bd.models import db, Factura

def test_clase_field():
    """Prueba el campo clase en el modelo Factura."""
    try:
        # Conectar a la base de datos
        db.init('../facturas.db')
        
        print("=== Prueba del campo 'clase' ===")
        
        # Verificar facturas existentes
        print("\n1. Facturas existentes con campo clase:")
        facturas = list(Factura.select())
        for f in facturas:
            print(f"   ID: {f.folio_interno}, Serie-Folio: {f.serie}-{f.folio}")
            print(f"   Clase: '{f.clase}' (tipo: {type(f.clase)})")
            print(f"   Emisor: {f.nombre_emisor}")
            print()
        
        # Actualizar una factura existente con clase
        if facturas:
            factura_test = facturas[0]
            print(f"2. Actualizando factura {factura_test.folio_interno} con clase='Prueba'")
            
            # Actualizar el campo clase
            factura_test.clase = "Prueba"
            factura_test.save()
            
            # Verificar que se guardó
            factura_reloaded = Factura.get(Factura.folio_interno == factura_test.folio_interno)
            print(f"   Clase después de guardar: '{factura_reloaded.clase}'")
            
            # Revertir el cambio
            factura_test.clase = None
            factura_test.save()
            print("   Cambio revertido (clase = None)")
            
        print("\n✅ Prueba del campo 'clase' completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clase_field()
