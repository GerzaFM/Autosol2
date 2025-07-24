#!/usr/bin/env python3
"""
Script para probar la funcionalidad de auto-relleno
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bd'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solicitudapp'))

from peewee import SqliteDatabase
from bd.models import Proveedor, Factura, Reparto
from solicitudapp.config.app_config import AppConfig

# Usar la base de datos del directorio raíz
db_path = os.path.join(os.path.dirname(__file__), '..', 'facturas.db')
db = SqliteDatabase(db_path)

# Configurar los modelos para usar esta base de datos
Proveedor._meta.database = db
Factura._meta.database = db
Reparto._meta.database = db

def test_autorelleno():
    """Probar la lógica de auto-relleno manualmente"""
    
    # Conectar a la base de datos
    db.connect()
    
    print("=== Test de Auto-relleno ===")
    
    # Buscar proveedor de prueba
    proveedor = "ROSAURA GUTIERREZ DUARTE"
    
    try:
        proveedor_bd = Proveedor.get(Proveedor.nombre == proveedor)
        print(f"✅ Proveedor encontrado: {proveedor_bd.nombre}")
        
        # Buscar la última factura del proveedor
        ultima_factura = (Factura
                        .select()
                        .where(Factura.proveedor == proveedor_bd)
                        .order_by(Factura.folio_interno.desc())
                        .first())
        
        if ultima_factura:
            print(f"✅ Última factura encontrada: {ultima_factura.folio_interno}")
            print(f"   Tipo: {ultima_factura.tipo}")
            
            # Buscar último reparto
            ultimo_reparto = (Reparto
                            .select()
                            .join(Factura)
                            .where(Factura.proveedor == proveedor_bd)
                            .order_by(Factura.folio_interno.desc())
                            .first())
            
            if ultimo_reparto:
                print(f"✅ Último reparto encontrado:")
                print(f"   Administracion: {ultimo_reparto.administracion}")
                print(f"   Comercial: {ultimo_reparto.comercial}")
                print(f"   Fleet: {ultimo_reparto.fleet}")
                print(f"   Seminuevos: {ultimo_reparto.seminuevos}")
                print(f"   Servicio: {ultimo_reparto.servicio}")
                print(f"   Refacciones: {ultimo_reparto.refacciones}")
                print(f"   HyP: {ultimo_reparto.hyp}")
                
                # Probar lógica del tipo
                if ultima_factura.tipo:
                    tipo_factura = ultima_factura.tipo.strip()
                    if " - " in tipo_factura:
                        clave_tipo = tipo_factura.split(" - ")[0]
                    else:
                        clave_tipo = tipo_factura
                    
                    if clave_tipo in AppConfig.TIPO_VALE:
                        tipo_sugerido = f"{clave_tipo} - {AppConfig.TIPO_VALE[clave_tipo]}"
                        print(f"✅ Tipo sugerido: {tipo_sugerido}")
                    else:
                        print(f"❌ Tipo no encontrado en diccionario: {clave_tipo}")
                
                print("\n🎉 Auto-relleno funcionará correctamente")
            else:
                print("❌ No se encontró reparto anterior")
        else:
            print("❌ No se encontró factura anterior")
            
    except Proveedor.DoesNotExist:
        print(f"❌ Proveedor '{proveedor}' no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_autorelleno()
