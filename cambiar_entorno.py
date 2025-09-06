#!/usr/bin/env python3
"""
Script para cambiar entre entornos de base de datos (TEST/PRODUCTION)
Uso: python cambiar_entorno.py [test|production]
"""

import sys
import re
from pathlib import Path

def cambiar_entorno(nuevo_entorno):
    """Cambia la variable ENVIRONMENT en settings.py"""
    
    if nuevo_entorno.lower() not in ['test', 'production']:
        print("❌ Error: El entorno debe ser 'test' o 'production'")
        return False
    
    # Ruta del archivo de configuración
    settings_file = Path('config/settings.py')
    
    if not settings_file.exists():
        print(f"❌ Error: No se encontró el archivo {settings_file}")
        return False
    
    # Leer archivo actual
    with open(settings_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y reemplazar la línea ENVIRONMENT
    patron = r"ENVIRONMENT\s*=\s*['\"][^'\"]*['\"]"
    nuevo_valor = f"ENVIRONMENT = '{nuevo_entorno.lower()}'"
    
    if re.search(patron, contenido):
        contenido_nuevo = re.sub(patron, nuevo_valor, contenido)
        
        # Escribir archivo modificado
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print(f"✅ Entorno cambiado exitosamente a: {nuevo_entorno.upper()}")
        
        # Mostrar configuración actual
        if nuevo_entorno.lower() == 'test':
            print("📋 Configuración TEST:")
            print("   • Host: localhost")
            print("   • Base de datos: tcm_matehuala")
            print("   • Usuario: postgres")
        else:
            print("📋 Configuración PRODUCTION:")
            print("   • Host: 10.90.101.51")
            print("   • Base de datos: autoforms")
            print("   • Usuario: sistemas")
        
        return True
    else:
        print("❌ Error: No se encontró la variable ENVIRONMENT en el archivo")
        return False

def mostrar_entorno_actual():
    """Muestra el entorno actualmente configurado"""
    settings_file = Path('config/settings.py')
    
    if not settings_file.exists():
        print(f"❌ Error: No se encontró el archivo {settings_file}")
        return
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    match = re.search(r"ENVIRONMENT\s*=\s*['\"]([^'\"]*)['\"]", contenido)
    if match:
        entorno_actual = match.group(1)
        print(f"📍 Entorno actual: {entorno_actual.upper()}")
        
        if entorno_actual.lower() == 'test':
            print("   → localhost/tcm_matehuala (postgres)")
        elif entorno_actual.lower() == 'production':
            print("   → 10.90.101.51/autoforms (sistemas)")
    else:
        print("❌ No se pudo determinar el entorno actual")

def main():
    print("🔄 CAMBIO DE ENTORNO DE BASE DE DATOS")
    print("=" * 45)
    
    if len(sys.argv) == 1:
        # Sin argumentos, mostrar entorno actual y opciones
        mostrar_entorno_actual()
        print("\n💡 Uso:")
        print("   python cambiar_entorno.py test        # Para entorno de pruebas")
        print("   python cambiar_entorno.py production  # Para entorno de producción")
        return
    
    elif len(sys.argv) == 2:
        nuevo_entorno = sys.argv[1]
        
        print("📋 Estado actual:")
        mostrar_entorno_actual()
        
        print(f"\n🔄 Cambiando a entorno: {nuevo_entorno.upper()}")
        if cambiar_entorno(nuevo_entorno):
            print("\n🎉 ¡Cambio completado! Reinicia la aplicación para aplicar cambios.")
        else:
            print("\n❌ Error al cambiar el entorno")
            sys.exit(1)
    
    else:
        print("❌ Error: Demasiados argumentos")
        print("💡 Uso: python cambiar_entorno.py [test|production]")
        sys.exit(1)

if __name__ == "__main__":
    main()
