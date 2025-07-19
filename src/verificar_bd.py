#!/usr/bin/env python3
"""
Script para verificar los datos en la base de datos
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bd'))

from peewee import SqliteDatabase
from bd.models import Proveedor, Factura, Reparto

# Usar la base de datos del directorio raíz
db_path = os.path.join(os.path.dirname(__file__), '..', 'facturas.db')
db = SqliteDatabase(db_path)

# Configurar los modelos para usar esta base de datos
Proveedor._meta.database = db
Factura._meta.database = db
Reparto._meta.database = db

def verificar_datos():
    """Verificar qué datos tenemos en la base de datos"""
    
    db.connect()
    
    print("=== Verificación de Base de Datos ===")
    
    try:
        # Contar registros
        count_proveedores = Proveedor.select().count()
        count_facturas = Factura.select().count()
        count_repartos = Reparto.select().count()
        
        print(f"Proveedores: {count_proveedores}")
        print(f"Facturas: {count_facturas}")
        print(f"Repartos: {count_repartos}")
        
        # Mostrar proveedores
        if count_proveedores > 0:
            print("\n--- Proveedores ---")
            for proveedor in Proveedor.select():
                print(f"ID: {proveedor.id}, Nombre: {proveedor.nombre}")
        
        # Mostrar facturas
        if count_facturas > 0:
            print("\n--- Facturas ---")
            for factura in Factura.select():
                print(f"Folio: {factura.folio_interno}, Proveedor: {factura.proveedor.nombre}, Tipo: {factura.tipo}")
        
        # Mostrar repartos
        if count_repartos > 0:
            print("\n--- Repartos ---")
            for reparto in Reparto.select():
                print(f"ID: {reparto.id}, Factura: {reparto.factura.folio_interno}, Servicio: {reparto.servicio}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_datos()