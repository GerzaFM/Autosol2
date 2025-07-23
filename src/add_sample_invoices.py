"""
Script para agregar más facturas de ejemplo con diferentes estados de cargada y pagada.
"""
import sys
import os

# Agregar el path de src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bd.models import db, Factura, Proveedor, Layout
import datetime

def add_sample_invoices():
    """Agrega facturas de ejemplo con diferentes estados."""
    try:
        print("=== Agregando Facturas de Ejemplo ===")
        
        # Configurar la ruta de la base de datos
        db_path = os.path.join('..', 'facturas.db')
        db_path = os.path.abspath(db_path)
        
        print(f"Conectando a BD: {db_path}")
        
        # Inicializar la conexión
        db.init(db_path)
        db.connect(reuse_if_open=True)
        
        # Obtener proveedor existente
        proveedor = Proveedor.get_by_id(1)
        
        # Crear facturas adicionales
        facturas_ejemplo = [
            {
                'folio_interno': 2,
                'serie': 1,
                'folio': 1002,
                'fecha': datetime.date(2025, 7, 20),
                'tipo': 'I',
                'nombre_emisor': 'Servicios Tecnológicos S.A.',
                'rfc_emisor': 'STE123456789',
                'nombre_receptor': 'TCM Matehuala S.A.',
                'rfc_receptor': 'TCM987654321',
                'subtotal': 2500.00,
                'ret_iva': 400.00,
                'ret_isr': 250.00,
                'iva_trasladado': 400.00,
                'total': 2250.00,
                'comentario': 'Servicios de desarrollo de software',
                'proveedor': proveedor,
                'cargada': False,  # No cargada
                'pagada': True     # Pero pagada
            },
            {
                'folio_interno': 3,
                'serie': 2,
                'folio': 2001,
                'fecha': datetime.date(2025, 7, 21),
                'tipo': 'I',
                'nombre_emisor': 'Materiales de Oficina S.A.',
                'rfc_emisor': 'MOF123456789',
                'nombre_receptor': 'TCM Matehuala S.A.',
                'rfc_receptor': 'TCM987654321',
                'subtotal': 850.00,
                'ret_iva': None,
                'ret_isr': None,
                'iva_trasladado': 136.00,
                'total': 986.00,
                'comentario': 'Compra de material de oficina',
                'proveedor': proveedor,
                'cargada': True,   # Cargada
                'pagada': True     # Y pagada
            },
            {
                'folio_interno': 4,
                'serie': 2,
                'folio': 2002,
                'fecha': datetime.date(2025, 7, 22),
                'tipo': 'I',
                'nombre_emisor': 'Consultores Empresariales S.C.',
                'rfc_emisor': 'CEE123456789',
                'nombre_receptor': 'TCM Matehuala S.A.',
                'rfc_receptor': 'TCM987654321',
                'subtotal': 5000.00,
                'ret_iva': 800.00,
                'ret_isr': 500.00,
                'iva_trasladado': 800.00,
                'total': 4500.00,
                'comentario': 'Consultoría empresarial - Julio 2025',
                'proveedor': proveedor,
                'cargada': False,  # No cargada
                'pagada': False    # No pagada
            }
        ]
        
        # Crear las facturas
        for datos in facturas_ejemplo:
            try:
                factura = Factura.create(**datos)
                estado_cargada = "Sí" if datos['cargada'] else "No"
                estado_pagada = "Sí" if datos['pagada'] else "No"
                print(f"✅ Factura {datos['serie']}-{datos['folio']} creada - Cargada: {estado_cargada}, Pagada: {estado_pagada}")
            except Exception as e:
                print(f"❌ Error creando factura {datos['serie']}-{datos['folio']}: {e}")
        
        # Mostrar resumen
        print(f"\n=== Resumen ===")
        total_facturas = Factura.select().count()
        facturas_cargadas = Factura.select().where(Factura.cargada == True).count()
        facturas_pagadas = Factura.select().where(Factura.pagada == True).count()
        
        print(f"Total de facturas: {total_facturas}")
        print(f"Facturas cargadas: {facturas_cargadas}")
        print(f"Facturas pagadas: {facturas_pagadas}")
        
        # Mostrar todas las facturas
        print(f"\n=== Todas las Facturas ===")
        for factura in Factura.select():
            cargada_str = "Sí" if factura.cargada else "No"
            pagada_str = "Sí" if factura.pagada else "No"
            print(f"ID: {factura.folio_interno}, Serie-Folio: {factura.serie}-{factura.folio}, "
                  f"Total: ${factura.total:,.2f}, Cargada: {cargada_str}, Pagada: {pagada_str}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    add_sample_invoices()
