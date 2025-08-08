#!/usr/bin/env python3
"""
Script para crear una función helper y corregir todos los .get().strip() problemáticos
"""
import os
import sys
import re

def safe_get_strip(data, key, default=''):
    """
    Función helper para obtener un valor de un dict y hacer strip de manera segura
    
    Args:
        data: Diccionario
        key: Clave a buscar
        default: Valor por defecto si la clave no existe
        
    Returns:
        str: Valor limpio (sin espacios) o string vacío
    """
    value = data.get(key, default)
    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()

def corregir_archivos_problematicos():
    """Agregar la función helper a los archivos que la necesitan"""
    
    archivos_a_corregir = [
        "src/buscarapp/autocarga/provider_matcher.py",
        "src/buscarapp/autocarga/autocarga.py"
    ]
    
    helper_function = '''
def safe_get_strip(data, key, default=''):
    """
    Función helper para obtener un valor de un dict y hacer strip de manera segura
    
    Args:
        data: Diccionario
        key: Clave a buscar
        default: Valor por defecto si la clave no existe
        
    Returns:
        str: Valor limpio (sin espacios) o string vacío
    """
    value = data.get(key, default)
    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()

'''
    
    for archivo in archivos_a_corregir:
        ruta_completa = archivo
        if os.path.exists(ruta_completa):
            print(f"📝 Procesando {archivo}")
            
            # Leer contenido actual
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar si ya tiene la función
            if 'def safe_get_strip(' not in contenido:
                # Buscar el lugar para insertar la función (después de los imports)
                lineas = contenido.split('\n')
                indice_insercion = 0
                
                # Encontrar el final de los imports
                for i, linea in enumerate(lineas):
                    if linea.strip().startswith('from ') or linea.strip().startswith('import '):
                        indice_insercion = i + 1
                    elif linea.strip() and not linea.strip().startswith('#'):
                        if not (linea.strip().startswith('from ') or linea.strip().startswith('import ')):
                            break
                
                # Insertar la función helper
                lineas.insert(indice_insercion, helper_function)
                contenido_nuevo = '\n'.join(lineas)
                
                # Guardar archivo modificado
                with open(ruta_completa, 'w', encoding='utf-8') as f:
                    f.write(contenido_nuevo)
                
                print(f"✅ Función helper agregada a {archivo}")
            else:
                print(f"⏭️  {archivo} ya tiene la función helper")
        else:
            print(f"❌ No se encontró {archivo}")

if __name__ == "__main__":
    print("=== CORRECCIÓN DE ARCHIVOS PROBLEMÁTICOS ===")
    corregir_archivos_problematicos()
    print("\n🎉 Corrección completada")
    print("📌 Ahora los archivos tienen una función helper para evitar errores con None.strip()")
