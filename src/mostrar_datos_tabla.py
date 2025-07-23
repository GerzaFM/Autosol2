#!/usr/bin/env python3
"""
Script para mostrar exactamente qué datos se cargan en la tabla
"""
import sys
import os
from bd.models import Factura, Proveedor, db

def mostrar_datos_tabla():
    """Muestra los datos tal como aparecerían en la tabla."""
    try:
        # Conectar a la base de datos
        db.init('../facturas.db')
        
        print("Datos que aparecerán en la tabla:")
        print("=" * 80)
        
        facturas_query = (Factura
                        .select()
                        .join(Proveedor, on=(Factura.proveedor == Proveedor.id))
                        .order_by(Factura.fecha.desc()))
        
        print(f"{'ID':<5} {'Tipo':<6} {'Fecha':<12} {'Emisor':<25} {'Total':<12} {'Clase':<15} {'Cargada':<8} {'Pagada':<8}")
        print("-" * 80)
        
        for factura in facturas_query:
            # Manejar la fecha de forma segura
            fecha_str = factura.fecha
            if hasattr(factura.fecha, 'strftime'):
                fecha_str = factura.fecha.strftime('%Y-%m-%d')
            elif isinstance(factura.fecha, str):
                fecha_str = factura.fecha
            else:
                fecha_str = str(factura.fecha)
            
            # Convertir booleanos a texto legible
            cargada_str = "Sí" if factura.cargada else "No"
            pagada_str = "Sí" if factura.pagada else "No"
            
            print(f"{factura.folio_interno:<5} {factura.tipo:<6} {fecha_str:<12} {factura.nombre_emisor[:25]:<25} ${factura.total:,.2f}{'':>4} {factura.clase or '':<15} {cargada_str:<8} {pagada_str:<8}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    mostrar_datos_tabla()
