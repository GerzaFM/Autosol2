"""
Script de prueba para verificar la conexión a la base de datos.
"""
import sys
import os

# Agregar el path de src
sys.path.append(os.path.join(os.path.dirname(__file__)))

from bd.models import db, Factura, Proveedor
from bd.bd_control import DBManager

def test_database():
    """Prueba la conexión y consultas a la base de datos."""
    try:
        print("=== Prueba de Conexión a Base de Datos ===")
        
        # Usar la base de datos de la raíz del proyecto
        db_path = os.path.join('..', 'facturas.db')
        db_path = os.path.abspath(db_path)
        
        if os.path.exists(db_path):
            print(f"Base de datos encontrada: {db_path}")
        else:
            print("❌ No se encontró el archivo de base de datos")
            return False
        
        # Inicializar la base de datos con la ruta correcta
        db.init(db_path)
        
        # Probar conexión
        db.connect(reuse_if_open=True)
        print("✅ Conexión establecida")
        
        # Contar registros
        factura_count = Factura.select().count()
        proveedor_count = Proveedor.select().count()
        
        print(f"📊 Facturas en la BD: {factura_count}")
        print(f"📊 Proveedores en la BD: {proveedor_count}")
        
        if factura_count > 0:
            print("\n=== Primeras 3 facturas ===")
            for factura in Factura.select().limit(3):
                print(f"ID: {factura.folio_interno}, Serie-Folio: {factura.serie}-{factura.folio}, "
                      f"Fecha: {factura.fecha}, Total: ${factura.total}")
        
        # Probar DBManager
        print("\n=== Probando DBManager ===")
        db_manager = DBManager()
        print("✅ DBManager inicializado correctamente")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()
