#!/usr/bin/env python3
"""
Script de prueba directo con archivos específicos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from buscarapp.autocarga.autocarga import AutoCarga

def test_autocarga_directo():
    """
    Prueba directa procesando archivos específicos de Pruebas.
    """
    print("🚀 PRUEBA DIRECTA DEL SISTEMA AUTOCARGA")
    print("=" * 60)
    
    # Crear instancia básica
    autocarga = AutoCarga()
    
    # Lista manual de archivos de prueba
    archivos_vales = [
        "Pruebas/8927 SERVICIO NAVA MEDRANO.pdf",
        "Pruebas/8954 SERVICIO NAVA MEDRANO.pdf"
    ]
    
    # Verificar que existen
    archivos_existentes = []
    for archivo in archivos_vales:
        if Path(archivo).exists():
            archivos_existentes.append(archivo)
            print(f"✅ Encontrado: {archivo}")
        else:
            print(f"❌ No encontrado: {archivo}")
    
    if not archivos_existentes:
        print("❌ No se encontraron archivos para procesar")
        return
    
    print(f"\n📄 Procesando {len(archivos_existentes)} archivos...")
    print("-" * 60)
    
    # Procesar vales directamente
    vales_dict = autocarga.procesar_vales(archivos_existentes)
    
    print("\n🎯 VERIFICACIÓN DE DESCRIPCIONES:")
    print("=" * 50)
    
    for vale_id, vale_data in vales_dict.items():
        print(f"\n📄 {vale_id}:")
        for campo, valor in vale_data.items():
            if valor:
                print(f"   ✅ {campo}: {valor}")
            else:
                print(f"   ❌ {campo}: (No encontrado)")
        
        # Destacar descripción
        descripcion = vale_data.get('Descripcion', '')
        if descripcion:
            print(f"   🎯 DESCRIPCIÓN EXTRAÍDA: ✅ {descripcion}")
        else:
            print(f"   🎯 DESCRIPCIÓN EXTRAÍDA: ❌ No encontrada")
    
    print("\n📊 RESUMEN FINAL:")
    print("-" * 30)
    print(f"✅ Archivos procesados: {len(archivos_existentes)}")
    print(f"✅ Vales extraídos: {len(vales_dict)}")
    
    # Verificar que todas las descripciones fueron extraídas
    vales_con_descripcion = sum(1 for vale in vales_dict.values() if vale.get('Descripcion'))
    print(f"📝 Vales con descripción: {vales_con_descripcion}/{len(vales_dict)}")
    
    if vales_con_descripcion == len(vales_dict) and len(vales_dict) > 0:
        print("🎉 ¡TODAS LAS DESCRIPCIONES FUERON EXTRAÍDAS CORRECTAMENTE!")
    elif vales_con_descripcion > 0:
        print("⚠️  Algunas descripciones fueron extraídas")
    else:
        print("❌ No se extrajeron descripciones")

if __name__ == "__main__":
    test_autocarga_directo()
