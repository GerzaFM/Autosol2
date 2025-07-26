#!/usr/bin/env python3
"""
Test específico para verificar la extracción de referencias
"""

import sys
import os
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def main():
    print("🔢 PRUEBA ESPECÍFICA - EXTRACCIÓN DE REFERENCIAS")
    print("=" * 60)
    
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
        
    print(f"\n🔄 Procesando {len(archivos_existentes)} archivos...\n")
    
    try:
        autocarga = AutoCarga()
        resultados = autocarga.procesar_vales(archivos_existentes)
        
        print(f'\n✅ Procesamiento completado.')
        print(f'📊 Resultados - Focus en Referencias:')
        
        for clave, datos in resultados.items():
            print(f"\n📋 Vale: {clave}")
            print(f"   🔢 Número: {datos.get('Numero', 'N/A')}")
            print(f"   🎯 Referencia: {datos.get('Referencia', 'N/A')} {'✅' if datos.get('Referencia') else '❌'}")
            print(f"   📅 Fecha: {datos.get('Fecha', 'N/A')}")
            print(f"   💰 Total: {datos.get('Total', 'N/A')}")
            print(f"   🏢 Proveedor: {datos.get('Nombre', 'N/A')}")
            print(f"   📝 Descripción: {datos.get('Descripcion', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
