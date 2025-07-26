#!/usr/bin/env python3
"""
Test específico para el nuevo vale de SERVICIOS GLOBALES ELYT
"""

import sys
import os
sys.path.append('src')

from buscarapp.autocarga.autocarga import AutoCarga

def main():
    print("🆕 PRUEBA ESPECÍFICA - NUEVO VALE SERVICIOS GLOBALES ELYT")
    print("=" * 70)
    
    # Archivo específico del nuevo vale
    archivo_nuevo = r"C:\QuiterWeb\cache\15gerzahin.flores_QRSVCMX_V152266_180646_CD.pdf"
    
    if not os.path.exists(archivo_nuevo):
        print(f"❌ No se encontró el archivo: {archivo_nuevo}")
        return
        
    print(f"📄 Procesando: {os.path.basename(archivo_nuevo)}")
    print()
    
    try:
        autocarga = AutoCarga()
        
        # Procesar solo este archivo
        resultados = autocarga.procesar_vales([archivo_nuevo])
        
        print(f'\n✅ Procesamiento completado.')
        print(f'📊 Resultados detallados:')
        
        for clave, datos in resultados.items():
            print(f"\n📋 Vale: {clave}")
            
            # Datos esperados vs extraídos
            datos_esperados = {
                'Nombre': 'SERVICIOS GLOBALES ELYT SA DE CV',
                'Numero': 'V152266',
                'Fecha': '18/07/2025',
                'Departamento': '6 ADMINISTRACION',
                'Sucursal': '15 NISSAN MATEHUALA',
                'Marca': '2 - NISSAN',
                'Responsable': '294379',
                'Tipo De Vale': 'VC VALE DE CONTROL',
                'Total': '12,837.49',
                'Descripcion': 'MARKETING DE EXPERIENCIA (INCLUYE EMBAJADORES DE EXPERIENCIA MAS AMENIDADES) DE ACUERDO A CONTRATO C-23'
            }
            
            for campo, valor_esperado in datos_esperados.items():
                valor_extraido = datos.get(campo, 'N/A')
                estado = '✅' if valor_extraido == valor_esperado else '⚠️' 
                print(f"   {campo:15}: {valor_extraido}")
                if valor_extraido != valor_esperado and valor_extraido != 'N/A':
                    print(f"                      Esperado: {valor_esperado}")
                    
            # Mostrar campos adicionales extraídos
            print(f"\n   📋 Otros campos extraídos:")
            for campo, valor in datos.items():
                if campo not in datos_esperados:
                    print(f"   {campo:15}: {valor}")
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
