"""
Script de prueba para verificar los datos disponibles en la base de datos 
para la función de reimprimir.
"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.bd.models import Factura, Proveedor, Concepto, Vale, db

def probar_datos_factura():
    """Prueba la obtención de datos de una factura para reimprimir."""
    try:
        db.connect()
        
        # Obtener la primera factura
        factura = Factura.select().first()
        if not factura:
            print("No hay facturas en la base de datos")
            return
        
        print("=== DATOS DE FACTURA PARA REIMPRESIÓN ===")
        print(f"Folio Interno: {factura.folio_interno}")
        print(f"Serie: {factura.serie}")
        print(f"Folio: {factura.folio}")
        print(f"Fecha: {factura.fecha}")
        print(f"Fecha Emisión: {factura.fecha_emision}")
        print(f"Tipo: {factura.tipo}")
        print(f"Emisor: {factura.nombre_emisor}")
        print(f"RFC Emisor: {factura.rfc_emisor}")
        print(f"Total: ${factura.total:,.2f}")
        
        # Obtener proveedor
        proveedor = factura.proveedor
        print(f"\n=== PROVEEDOR ===")
        print(f"Nombre: {proveedor.nombre}")
        print(f"RFC: {proveedor.rfc}")
        print(f"Email: {proveedor.email}")
        print(f"Teléfono: {proveedor.telefono}")
        
        # Obtener conceptos
        conceptos = list(factura.conceptos)
        print(f"\n=== CONCEPTOS ({len(conceptos)}) ===")
        for concepto in conceptos:
            print(f"- {concepto.cantidad} x {concepto.descripcion} = ${concepto.precio_unitario:,.2f}")
        
        # Verificar vale
        try:
            vale = Vale.get(Vale.factura == factura.folio_interno)
            print(f"\n=== VALE ===")
            print(f"No Vale: {vale.noVale}")
        except:
            print(f"\n=== VALE ===")
            print("No hay vale asociado")
        
        print(f"\n✅ Datos listos para reimpresión")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    probar_datos_factura()
