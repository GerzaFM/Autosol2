"""
Agregar conceptos de ejemplo a las facturas existentes.
"""
import sys
import os
sys.path.append('src')

from bd.models import Factura, Concepto, db

def main():
    print("=== Agregando conceptos de ejemplo ===")
    
    try:
        db.connect()
        
        # Buscar facturas por serie-folio
        facturas = {
            "1-1002": None,
            "2-2001": None, 
            "2-2002": None
        }
        
        for factura in Factura.select():
            serie_folio = f"{factura.serie}-{factura.folio}"
            if serie_folio in facturas:
                facturas[serie_folio] = factura
        
        # Agregar conceptos a la factura 1-1002
        if facturas["1-1002"]:
            print("Agregando conceptos a factura 1-1002...")
            Concepto.create(
                descripcion="Servicios profesionales de consultoría",
                cantidad=1,
                precio_unitario=1500.00,
                total=1500.00,
                factura=facturas["1-1002"]
            )
            Concepto.create(
                descripcion="Capacitación técnica especializada", 
                cantidad=1,
                precio_unitario=750.00,
                total=750.00,
                factura=facturas["1-1002"]
            )
            print("✅ Conceptos agregados a 1-1002")
        
        # Agregar conceptos a la factura 2-2001
        if facturas["2-2001"]:
            print("Agregando conceptos a factura 2-2001...")
            Concepto.create(
                descripcion="Suministro de materiales de oficina",
                cantidad=50,
                precio_unitario=15.50,
                total=775.00,
                factura=facturas["2-2001"]
            )
            Concepto.create(
                descripcion="Equipos de cómputo y accesorios",
                cantidad=2,
                precio_unitario=105.50,
                total=211.00,
                factura=facturas["2-2001"]
            )
            print("✅ Conceptos agregados a 2-2001")
            
        # Agregar conceptos a la factura 2-2002
        if facturas["2-2002"]:
            print("Agregando conceptos a factura 2-2002...")
            Concepto.create(
                descripcion="Servicios de mantenimiento preventivo",
                cantidad=1,
                precio_unitario=2500.00,
                total=2500.00,
                factura=facturas["2-2002"]
            )
            Concepto.create(
                descripcion="Reparación de equipos especializados",
                cantidad=1,
                precio_unitario=1500.00,
                total=1500.00,
                factura=facturas["2-2002"]
            )
            Concepto.create(
                descripcion="Repuestos y componentes",
                cantidad=5,
                precio_unitario=100.00,
                total=500.00,
                factura=facturas["2-2002"]
            )
            print("✅ Conceptos agregados a 2-2002")
        
        print("\n=== Verificación final ===")
        for f in Factura.select():
            conceptos = list(f.conceptos)
            print(f'Factura {f.serie}-{f.folio}: {len(conceptos)} conceptos')
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    main()
