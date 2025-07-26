#!/usr/bin/env python3
"""
Script de prueba completo del sistema AutoCarga con descripción
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.autocarga import AutoCarga

def test_autocarga_completo():
    """
    Prueba completa del sistema AutoCarga incluyendo descripción.
    """
    print("🚀 PRUEBA COMPLETA DEL SISTEMA AUTOCARGA")
    print("=" * 60)
    
    # Crear instancia de AutoCarga
    # Usar la carpeta Pruebas como fuente
    autocarga = AutoCarga(ruta_carpeta="Pruebas", dias_atras=30)
    
    # Ejecutar autocarga
    vales, ordenes = autocarga.ejecutar_autocarga()
    
    print("\n🎯 VERIFICACIÓN DE DESCRIPCIONES EN VALES:")
    print("=" * 50)
    
    for vale_id, vale_data in vales.items():
        print(f"\n📄 {vale_id}:")
        for campo, valor in vale_data.items():
            print(f"   {campo}: {valor}")
        
        # Destacar descripción si existe
        descripcion = vale_data.get('Descripcion', '')
        if descripcion:
            print(f"   🎯 DESCRIPCIÓN: {descripcion}")
    
    print("\n📊 RESUMEN FINAL:")
    print("-" * 30)
    print(f"✅ Vales procesados: {len(vales)}")
    print(f"✅ Órdenes procesadas: {len(ordenes)}")
    
    # Verificar que todas las descripciones fueron extraídas
    vales_con_descripcion = sum(1 for vale in vales.values() if vale.get('Descripcion'))
    print(f"📝 Vales con descripción: {vales_con_descripcion}/{len(vales)}")
    
    if vales_con_descripcion == len(vales) and len(vales) > 0:
        print("🎉 ¡TODAS LAS DESCRIPCIONES FUERON EXTRAÍDAS CORRECTAMENTE!")
    elif vales_con_descripcion > 0:
        print("⚠️  Algunas descripciones fueron extraídas")
    else:
        print("❌ No se extrajeron descripciones")

if __name__ == "__main__":
    test_autocarga_completo()
