#!/usr/bin/env python3
"""
Test para verificar que se muestren correctamente los tipos de vale
"""
import sqlite3
import sys
import os

# Agregar src al path  
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from bd.models import Vale, Factura
from solicitudapp.config.app_config import AppConfig

def test_mostrar_tipos_correctos():
    print("=== TEST DE TIPOS DE VALE CORREGIDOS ===")
    
    # 1. Obtener facturas de NAVA MEDRANO con vales asociados
    print("\n1. FACTURAS NAVA CON VALES ASOCIADOS:")
    facturas_con_vales = (Factura
                         .select()
                         .join(Vale, on=(Factura.folio_interno == Vale.factura_id))
                         .where(Factura.nombre_emisor.contains('NAVA'))
                         .distinct())
    
    for factura in facturas_con_vales:
        print(f"   📄 Factura {factura.folio_interno}: {factura.nombre_emisor}")
        
        # Obtener vale asociado
        try:
            vale = Vale.get(Vale.factura_id == factura.folio_interno)
            tipo_desc = AppConfig.TIPO_VALE.get(vale.tipo, vale.tipo)
            
            print(f"      💳 Vale: {vale.noVale}")
            print(f"      🏷️ Tipo: {vale.tipo} → {tipo_desc}")
            print(f"      💰 Total: {vale.total}")
            print(f"      📝 Descripción: {vale.descripcion}")
            print()
            
        except Vale.DoesNotExist:
            print(f"      ❌ Sin vale asociado")
    
    # 2. Simular lo que mostraría el info panel
    print("\n2. SIMULACIÓN DE INFO PANEL:")
    factura_ejemplo = facturas_con_vales.first()
    if factura_ejemplo:
        vale_ejemplo = Vale.get(Vale.factura_id == factura_ejemplo.folio_interno)
        
        # Esto es lo que se mostraría en el panel
        info_panel_data = {
            "TIPO DE VALE": f"{vale_ejemplo.tipo} - {AppConfig.TIPO_VALE.get(vale_ejemplo.tipo, vale_ejemplo.tipo)}",
            "NÚMERO DE VALE": vale_ejemplo.noVale,
            "DESCRIPCIÓN": vale_ejemplo.descripcion,
            "TOTAL": vale_ejemplo.total,
            "PROVEEDOR": vale_ejemplo.proveedor,
            "CUENTA": vale_ejemplo.cuenta,
            "FECHA": vale_ejemplo.fechaVale
        }
        
        print(f"   Para factura {factura_ejemplo.folio_interno}:")
        for campo, valor in info_panel_data.items():
            print(f"      {campo}: {valor}")

if __name__ == "__main__":
    test_mostrar_tipos_correctos()
