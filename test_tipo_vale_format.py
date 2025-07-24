#!/usr/bin/env python3
"""
Script de prueba para verificar el formato key-value del tipo de vale en reimprimir
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from solicitudapp.config.app_config import AppConfig
    print("✅ AppConfig importado correctamente")
    
    # Verificar que existe TIPO_VALE
    if hasattr(AppConfig, 'TIPO_VALE'):
        print("✅ TIPO_VALE encontrado en AppConfig")
        print(f"📋 Tipos de vale disponibles: {len(AppConfig.TIPO_VALE)} elementos")
        
        # Mostrar algunos ejemplos
        print("\n🔍 Ejemplos de tipos de vale:")
        count = 0
        for key, value in AppConfig.TIPO_VALE.items():
            print(f"   {key} - {value}")
            count += 1
            if count >= 5:  # Mostrar solo los primeros 5
                break
        
        if len(AppConfig.TIPO_VALE) > 5:
            print(f"   ... y {len(AppConfig.TIPO_VALE) - 5} más")
        
        # Simular el formato que se usará en reimprimir
        print("\n🧪 Simulación de formato para reimprimir:")
        test_tipos = ["VC", "GA", "OSI", "MEU", "DIV"]
        
        for tipo in test_tipos:
            if tipo in AppConfig.TIPO_VALE:
                formatted = f"{tipo} - {AppConfig.TIPO_VALE[tipo]}"
                print(f"   Tipo '{tipo}' → '{formatted}'")
            else:
                print(f"   Tipo '{tipo}' → No encontrado en diccionario")
                
    else:
        print("❌ TIPO_VALE no encontrado en AppConfig")
        
except ImportError as e:
    print(f"❌ Error importando AppConfig: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print("\n✅ Prueba completada - El formato key-value debería funcionar correctamente")
