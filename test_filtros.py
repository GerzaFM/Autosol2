"""
Script de prueba para verificar que los filtros funcionan correctamente
"""
import sys
import os
sys.path.append('src')

from bd.models import Factura, Proveedor, Concepto, db

def main():
    print("=== Estado de facturas para filtros ===")
    
    try:
        db.connect()
        
        print("Facturas en base de datos:")
        for f in Factura.select().join(Proveedor):
            print(f"ID: {f.folio_interno}")
            print(f"  Serie-Folio: {f.serie}-{f.folio}")
            print(f"  Fecha: {f.fecha}")
            print(f"  Tipo: {f.tipo}")
            print(f"  Emisor: {f.nombre_emisor}")
            print(f"  Proveedor: {f.proveedor.nombre}")
            print(f"  Cargada: {f.cargada}")
            print(f"  Pagada: {f.pagada}")
            
            # Mostrar conceptos
            conceptos = list(f.conceptos)
            if conceptos:
                conceptos_str = " / ".join([c.descripcion for c in conceptos])
                print(f"  Conceptos: {conceptos_str}")
            print()
        
        print("Proveedores disponibles:")
        for p in Proveedor.select().order_by(Proveedor.nombre):
            print(f"- {p.nombre} (RFC: {p.rfc})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    main()
