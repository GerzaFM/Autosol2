"""
Script para inicializar y crear las tablas de la base de datos.
"""
import sys
import os

# Agregar el path de src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bd.models import db, Factura, Proveedor, Layout
from bd.bd_control import DBManager
import datetime

def init_database():
    """Inicializa la base de datos y crea las tablas."""
    try:
        print("=== Inicialización de Base de Datos ===")
        
        # Configurar la ruta de la base de datos
        db_path = os.path.join('..', 'facturas.db')  # Usar la del directorio raíz
        db_path = os.path.abspath(db_path)
        
        print(f"Inicializando BD en: {db_path}")
        
        # Inicializar la conexión
        db.init(db_path)
        db.connect(reuse_if_open=True)
        
        # Crear las tablas
        print("Creando tablas...")
        tables_to_create = [Proveedor, Layout, Factura]
        db.create_tables(tables_to_create, safe=True)
        print("✅ Tablas creadas exitosamente")
        
        # Verificar las tablas
        print("\n=== Verificando tablas ===")
        for table in tables_to_create:
            count = table.select().count()
            print(f"Tabla {table.__name__}: {count} registros")
        
        # Crear algunos datos de ejemplo si no existen
        if Proveedor.select().count() == 0:
            print("\n=== Creando datos de ejemplo ===")
            
            # Crear proveedor de ejemplo
            proveedor_ejemplo = Proveedor.create(
                id=1,
                nombre="Proveedor Ejemplo S.A. de C.V.",
                rfc="PEJ123456789",
                telefono="444-123-4567",
                email="contacto@ejemplo.com",
                nombre_contacto="Juan Pérez"
            )
            
            # Crear layout de ejemplo
            layout_ejemplo = Layout.create(
                id=1,
                nombre="Layout Principal",
                fecha=datetime.date.today()
            )
            
            # Crear factura de ejemplo
            factura_ejemplo = Factura.create(
                folio_interno=1,
                serie=1,
                folio=1001,
                fecha=datetime.date.today(),
                tipo="I",
                nombre_emisor="Proveedor Ejemplo S.A. de C.V.",
                rfc_emisor="PEJ123456789",
                nombre_receptor="Mi Empresa S.A. de C.V.",
                rfc_receptor="MEE987654321",
                subtotal=1000.00,
                ret_iva=160.00,
                ret_isr=100.00,
                iva_trasladado=160.00,
                total=900.00,
                comentario="Factura de ejemplo para pruebas",
                proveedor=proveedor_ejemplo,
                layout=layout_ejemplo
            )
            
            print("✅ Datos de ejemplo creados")
        
        # Verificar datos finales
        print("\n=== Estado Final ===")
        factura_count = Factura.select().count()
        proveedor_count = Proveedor.select().count()
        print(f"📊 Facturas: {factura_count}")
        print(f"📊 Proveedores: {proveedor_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_database()
