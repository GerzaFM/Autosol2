#!/usr/bin/env python3
"""
Test específico para el vale de la impresora
"""

import sys
import os
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def main():
    print("🖨️ PRUEBA ESPECÍFICA - VALE IMPRESORA")
    print("=" * 50)
    
    # Archivo específico de la impresora
    archivo_impresora = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152885_182280_CD.pdf"
    
    if not os.path.exists(archivo_impresora):
        print(f"❌ No se encontró el archivo: {archivo_impresora}")
        return
        
    print(f"📄 Procesando: {os.path.basename(archivo_impresora)}")
    print()
    
    try:
        autocarga = AutoCarga()
        
        # Procesar solo este archivo
        resultados = autocarga.procesar_vales([archivo_impresora])
        
        print(f'\n✅ Procesamiento completado.')
        print(f'📊 Resultados detallados:')
        
        for clave, datos in resultados.items():
            print(f"\n📋 Vale: {clave}")
            for campo, valor in datos.items():
                if campo == 'Descripcion':
                    print(f"   🎯 {campo}: {valor} {'✅' if valor and valor != 'MATEHUALA' else '❌'}")
                else:
                    print(f"   📝 {campo}: {valor}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
