"""
Script principal para ejecutar el sistema AutoCarga mejorado.
Demuestra cómo usar la extracción de datos y la comparación de proveedores.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from autocarga import AutoCarga


def main():
    """
    Función principal que ejecuta el sistema AutoCarga completo.
    """
    print("🚀 SISTEMA AUTOCARGA - EXTRACCIÓN Y COMPARACIÓN DE PROVEEDORES")
    print("=" * 80)
    print(f"⏰ Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configuración
    RUTA_CARPETA = r"C:\QuiterWeb\cache"
    DIAS_ATRAS = 3  # Buscar archivos de los últimos 3 días
    CARPETA_SALIDA = "resultados_autocarga"
    
    print(f"📂 Carpeta de búsqueda: {RUTA_CARPETA}")
    print(f"📅 Período: Últimos {DIAS_ATRAS} días")
    print(f"📁 Carpeta de salida: {CARPETA_SALIDA}")
    print()
    
    try:
        # Crear carpeta de salida si no existe
        os.makedirs(CARPETA_SALIDA, exist_ok=True)
        
        # Crear instancia de AutoCarga
        autocarga = AutoCarga(
            ruta_carpeta=RUTA_CARPETA,
            dias_atras=DIAS_ATRAS
        )
        
        print("🔄 Iniciando procesamiento...")
        print()
        
        # Ejecutar el proceso completo
        vales, ordenes = autocarga.ejecutar_autocarga()
        
        print("\n" + "📊 PROCESAMIENTO COMPLETADO")
        print("=" * 60)
        
        # Guardar resultados
        print("💾 Guardando archivos de resultados...")
        ruta_vales, ruta_ordenes = autocarga.guardar_resultados(CARPETA_SALIDA)
        
        # Mostrar resumen final
        stats = autocarga.obtener_estadisticas()
        
        print(f"\n📈 RESUMEN FINAL:")
        print(f"   💳 Vales encontrados: {stats['vales_encontrados']}")
        print(f"   💳 Vales procesados exitosamente: {stats['vales_exitosos']}")
        print(f"   📋 Órdenes encontradas: {stats['ordenes_encontradas']}")
        print(f"   📋 Órdenes procesadas exitosamente: {stats['ordenes_exitosas']}")
        
        if 'provider_matching' in stats:
            pm = stats['provider_matching']
            print(f"   🔍 Vales con proveedor encontrado: {pm['vales_con_proveedor']}")
            print(f"   🔍 Órdenes con proveedor encontrado: {pm['ordenes_con_proveedor']}")
            print(f"   🔄 Proveedores actualizados con código: {pm['proveedores_actualizados']}")
        
        # Mostrar archivos generados
        print(f"\n📁 ARCHIVOS GENERADOS:")
        if ruta_vales:
            print(f"   💳 Vales: {ruta_vales}")
        if ruta_ordenes:
            print(f"   📋 Órdenes: {ruta_ordenes}")
        
        # Mostrar proveedores que podrían actualizarse
        actualizaciones = autocarga.obtener_proveedores_para_actualizar()
        if actualizaciones:
            print(f"\n🔄 PROVEEDORES CANDIDATOS PARA ACTUALIZACIÓN ({len(actualizaciones)}):")
            for act in actualizaciones[:10]:  # Mostrar solo los primeros 10
                print(f"   • {act['nombre']}")
                print(f"     Código propuesto: {act['codigo_propuesto']} (desde {act['fuente']})")
            
            if len(actualizaciones) > 10:
                print(f"   ... y {len(actualizaciones) - 10} más")
        
        print(f"\n✅ PROCESAMIENTO COMPLETO")
        print(f"🎯 Para actualizar proveedores en la BD, revisa los archivos generados")
        print(f"📋 Los nombres se mantienen con espacios como vienen del PDF")
        print(f"🔍 La comparación se hace sin espacios para encontrar coincidencias")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL PROCESAMIENTO:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def mostrar_ayuda():
    """
    Muestra información de ayuda sobre el sistema.
    """
    print("""
🔧 SISTEMA AUTOCARGA - AYUDA
============================

Este sistema busca y procesa automáticamente archivos PDF de:
• Vales (archivos QRSVCMX*)
• Órdenes (archivos QRSOPMX208*)

CARACTERÍSTICAS PRINCIPALES:
📄 Extrae datos manteniendo nombres con espacios como vienen del PDF
🔍 Compara con proveedores en BD sin espacios para encontrar coincidencias
🔄 Actualiza automáticamente códigos QuiteR faltantes en proveedores
💾 Genera archivos JSON con todos los datos extraídos
📊 Proporciona estadísticas detalladas del procesamiento

CONFIGURACIÓN:
• Modifica RUTA_CARPETA para cambiar dónde buscar archivos
• Ajusta DIAS_ATRAS para cambiar el período de búsqueda
• Cambia CARPETA_SALIDA para guardar resultados en otra ubicación

ARCHIVOS GENERADOS:
• vales_autocarga_[timestamp].json - Datos de vales procesados
• ordenes_autocarga_[timestamp].json - Datos de órdenes procesadas

Para más información, revisa el código fuente o ejecuta test_autocarga.py
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        mostrar_ayuda()
    else:
        success = main()
        
        if success:
            print(f"\n🎉 ¡Proceso completado exitosamente!")
        else:
            print(f"\n💥 El proceso falló. Revisa los errores arriba.")
            sys.exit(1)
