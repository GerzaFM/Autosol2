#!/usr/bin/env python3
"""
Test completo con ambos vales: impresora y herramientas
"""

import sys
import os
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def main():
    print("🧪 PRUEBA COMPLETA - IMPRESORA Y HERRAMIENTAS")
    print("=" * 55)
    
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
        print(f'📊 Resultados detallados por archivo:')
        
        for clave, datos in resultados.items():
            print(f"\n📋 Vale: {clave}")
            descripcion = datos.get('Descripcion', 'N/A')
            
            # Determinar si la descripción es correcta
            if 'IMPRESORA' in descripcion.upper():
                es_correcta = 'CABLES' in descripcion.upper() and 'MATEHUALA' not in descripcion.upper()
                print(f"   🖨️  Tipo: IMPRESORA")
            elif 'HERRAMIENTAS' in descripcion.upper():
                es_correcta = 'TRABAJO' in descripcion.upper() and 'MATEHUALA' not in descripcion.upper()
                print(f"   🔧 Tipo: HERRAMIENTAS")
            else:
                es_correcta = False
                print(f"   ❓ Tipo: DESCONOCIDO")
            
            print(f"   🎯 Descripción: {descripcion} {'✅' if es_correcta else '❌'}")
            print(f"   💰 Total: {datos.get('Total', 'N/A')}")
            print(f"   🏢 Proveedor: {datos.get('Nombre', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
