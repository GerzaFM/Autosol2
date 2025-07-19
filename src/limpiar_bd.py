#!/usr/bin/env python3
"""
Script para limpiar la base de datos de prueba.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from bd.models import Factura, Proveedor, Concepto, Reparto
    
    print("🧹 Limpiando base de datos...")
    
    # Eliminar todas las tablas relacionadas
    Concepto.delete().execute()
    Reparto.delete().execute()
    Factura.delete().execute()
    Proveedor.delete().execute()
    
    print("✅ Base de datos limpiada")
    
except Exception as e:
    print(f"❌ Error: {e}")
