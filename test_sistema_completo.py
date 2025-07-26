#!/usr/bin/env python3
"""
Script de prueba del sistema AutoCarga completo con archivos reales
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.autocarga import AutoCarga

def test_sistema_completo():
    """
    Prueba completa del sistema AutoCarga con archivos reales.
    """
    print("🚀 PRUEBA SISTEMA AUTOCARGA COMPLETO")
    print("=" * 60)
    
    # Crear instancia de AutoCarga con configuración por defecto
    # que busca en C:\QuiterWeb\cache
    autocarga = AutoCarga(ruta_carpeta=r"C:\QuiterWeb\cache", dias_atras=7)
    
    # Ejecutar autocarga completa
    print("🔥 Ejecutando autocarga...")
    vales, ordenes = autocarga.ejecutar_autocarga()
    
    print("\n🎯 VERIFICACIÓN DETALLADA DE VALES:")
    print("=" * 60)
    
    if vales:
        for vale_id, vale_data in vales.items():
            print(f"\n📄 Vale: {vale_id}")
            print("-" * 40)
            for campo, valor in vale_data.items():
                if valor:
                    print(f"   ✅ {campo}: {valor}")
                else:
                    print(f"   ❌ {campo}: (No encontrado)")
            
            # Destacar descripción
            descripcion = vale_data.get('Descripcion', '')
            if descripcion:
                print(f"   🎯 DESCRIPCIÓN: ✅ {descripcion}")
            else:
                print(f"   🎯 DESCRIPCIÓN: ❌ No encontrada")
    else:
        print("❌ No se procesaron vales")
    
    print("\n📊 RESUMEN FINAL:")
    print("=" * 40)
    print(f"✅ Vales procesados: {len(vales)}")
    print(f"✅ Órdenes procesadas: {len(ordenes)}")
    
    # Verificar descripciones
    if vales:
        vales_con_descripcion = sum(1 for vale in vales.values() if vale.get('Descripcion'))
        porcentaje = (vales_con_descripcion / len(vales)) * 100
        print(f"📝 Vales con descripción: {vales_con_descripcion}/{len(vales)} ({porcentaje:.1f}%)")
        
        if vales_con_descripcion == len(vales):
            print("🎉 ¡TODAS LAS DESCRIPCIONES EXTRAÍDAS CORRECTAMENTE!")
        elif vales_con_descripcion > 0:
            print("⚠️  Algunas descripciones extraídas")
        else:
            print("❌ No se extrajeron descripciones")
    
    # Mostrar estadísticas
    stats = autocarga.obtener_estadisticas()
    print(f"\n📈 ESTADÍSTICAS DETALLADAS:")
    print(f"   ⏰ Timestamp: {stats['timestamp']}")
    print(f"   📁 Vales encontrados: {stats['vales_encontrados']}")
    print(f"   🔄 Vales procesados: {stats['vales_procesados']}")
    print(f"   ✅ Vales exitosos: {stats['vales_exitosos']}")
    print(f"   ❌ Errores vales: {stats['errores_vales']}")

if __name__ == "__main__":
    test_sistema_completo()
