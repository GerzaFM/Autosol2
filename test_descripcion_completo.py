#!/usr/bin/env python3
"""
Script para probar la extracción completa de descripciones en vales
"""

import sys
import os
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def main():
    print("🧪 PRUEBA COMPLETA DE EXTRACCIÓN DE DESCRIPCIONES")
    print("=" * 60)
    
    # Test con archivos de la carpeta Pruebas
    carpeta_pruebas = 'Pruebas'
    if not os.path.exists(carpeta_pruebas):
        print(f"❌ No se encontró la carpeta {carpeta_pruebas}")
        return
        
    archivos_pdf = [f for f in os.listdir(carpeta_pruebas) if f.endswith('.pdf')]
    print(f'📂 Encontrados {len(archivos_pdf)} archivos PDF para procesar:')
    for archivo in archivos_pdf:
        print(f'  • {archivo}')

    print('\n🔄 Iniciando procesamiento...\n')
    
    try:
        autocarga = AutoCarga(ruta_carpeta=carpeta_pruebas)
        
        # Obtener lista de archivos completa
        lista_vales = [os.path.join(carpeta_pruebas, archivo) for archivo in archivos_pdf]
        
        # Procesar vales
        resultados = autocarga.procesar_vales(lista_vales)
        print(f'\n✅ Procesamiento completado.')
        print(f'📊 Resultados: {resultados}')
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
