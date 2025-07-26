#!/usr/bin/env python3
"""
Verificar que los tipos corregidos coincidan con TIPO_VALE
"""
import sqlite3
import sys
import os

# Agregar src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from solicitudapp.config.app_config import AppConfig
    print("✅ AppConfig cargado exitosamente")
except ImportError as e:
    print(f"❌ Error importando AppConfig: {e}")
    sys.exit(1)

def verificar_tipos_corregidos():
    print("=== VERIFICANDO TIPOS CORREGIDOS CON TIPO_VALE ===")
    
    conn = sqlite3.connect('facturas.db')
    cursor = conn.cursor()
    
    # Obtener tipos únicos de vales NAVA
    cursor.execute("SELECT DISTINCT tipo FROM vale WHERE proveedor LIKE '%NAVA%'")
    tipos_bd = [t[0] for t in cursor.fetchall()]
    
    print(f"\n1. TIPOS EN BD (vales NAVA): {tipos_bd}")
    
    print(f"\n2. VERIFICACIÓN CON TIPO_VALE:")
    for tipo in tipos_bd:
        descripcion = AppConfig.TIPO_VALE.get(tipo, "❌ NO ENCONTRADO")
        estado = "✅" if tipo in AppConfig.TIPO_VALE else "❌"
        print(f"   {estado} {tipo} → {descripcion}")
    
    # Mostrar vales específicos con sus tipos
    print(f"\n3. VALES NAVA CON TIPOS CORREGIDOS:")
    cursor.execute("""
        SELECT noVale, tipo, proveedor 
        FROM vale 
        WHERE proveedor LIKE '%NAVA%'
        ORDER BY tipo, noVale
    """)
    
    for vale in cursor.fetchall():
        tipo_desc = AppConfig.TIPO_VALE.get(vale[1], "Desconocido")
        print(f"   💳 {vale[0]} → {vale[1]} ({tipo_desc})")
    
    conn.close()

if __name__ == "__main__":
    verificar_tipos_corregidos()
