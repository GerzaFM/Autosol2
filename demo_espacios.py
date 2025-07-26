#!/usr/bin/env python3
"""
Script para demostrar la mejora de espacios en las descripciones extraídas
"""

import sys
import os
import re
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def mejorar_espacios_descripcion(descripcion: str) -> str:
    """
    Añade espacios lógicos a las descripciones extraídas.
    
    Args:
        descripcion (str): Descripción original sin espacios
        
    Returns:
        str: Descripción con espacios mejorados
    """
    if not descripcion:
        return descripcion
    
    # Reglas específicas para mejorar espacios
    mejoras = [
        # Regla 1: Separar marcas conocidas
        (r'IMPRESORA', 'IMPRESORA '),
        (r'HP', ' HP '),
        (r'LASERJET', ' LASERJET '),
        (r'M(\d+)W', r' M\1W'),
        
        # Regla 2: Separar antes de números de modelo
        (r'([A-Z])(\d)', r'\1 \2'),
        
        # Regla 3: Separar antes de comas
        (r',', ', '),
        
        # Regla 4: Separar palabras comunes
        (r'HERRAMIENTAS', 'HERRAMIENTAS '),
        (r'DE', ' DE '),
        (r'TRABAJO', ' TRABAJO'),
        
        # Regla 5: Separar CABLES
        (r'CABLES', ' CABLES'),
    ]
    
    resultado = descripcion
    
    # Aplicar cada regla
    for patron, reemplazo in mejoras:
        resultado = re.sub(patron, reemplazo, resultado)
    
    # Limpiar espacios excesivos
    resultado = re.sub(r'\s+', ' ', resultado).strip()
    
    return resultado

def main():
    print("🔤 DEMOSTRACIÓN DE MEJORA DE ESPACIOS")
    print("=" * 50)
    
    # Archivos específicos
    archivos = [
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf",  # Impresora
        r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V153597_183460_CD.pdf"   # Herramientas
    ]
    
    archivos_existentes = []
    for archivo in archivos:
        if os.path.exists(archivo):
            archivos_existentes.append(archivo)
            print(f"✅ Encontrado: {os.path.basename(archivo)}")
        else:
            print(f"❌ No encontrado: {os.path.basename(archivo)}")
    
    if not archivos_existentes:
        print("❌ No se encontraron archivos para procesar")
        return
        
    print(f"\n� Procesando {len(archivos_existentes)} archivos...\n")
    
    try:
        autocarga = AutoCarga()
        resultados = autocarga.procesar_vales(archivos_existentes)
        
        print(f'✅ Procesamiento completado.')
        print(f'📊 Comparación de descripciones:')
        
        for clave, datos in resultados.items():
            descripcion_original = datos.get('Descripcion', 'N/A')
            descripcion_mejorada = mejorar_espacios_descripcion(descripcion_original)
            
            print(f"\n📋 Vale: {clave}")
            print(f"   📝 Original:  '{descripcion_original}'")
            print(f"   ✨ Mejorada:  '{descripcion_mejorada}'")
            print(f"   📊 Mejora: {'✅ Sí' if descripcion_original != descripcion_mejorada else '❌ No necesaria'}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
