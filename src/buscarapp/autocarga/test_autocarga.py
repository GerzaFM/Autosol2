"""
Script de prueba para el sistema de AutoCarga mejorado.
Prueba la extracción de datos y la comparación de proveedores.
"""

import sys
import os
from pathlib import Path

# Agregar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from autocarga import AutoCarga
from provider_matcher import ProviderMatcher


def test_autocarga_completa():
    """
    Prueba completa del sistema de AutoCarga.
    """
    print("🚀 PRUEBA COMPLETA DEL SISTEMA AUTOCARGA")
    print("=" * 60)
    
    # Crear instancia de AutoCarga
    autocarga = AutoCarga(
        ruta_carpeta=r"C:\QuiterWeb\cache",
        dias_atras=7  # Buscar en la última semana
    )
    
    try:
        # Ejecutar el proceso completo
        vales, ordenes = autocarga.ejecutar_autocarga()
        
        print("\n" + "📊 RESULTADOS DEL PROCESAMIENTO:")
        print("=" * 60)
        print(f"💳 Vales procesados: {len(vales)}")
        print(f"📋 Órdenes procesadas: {len(ordenes)}")
        
        # Mostrar algunos ejemplos de datos extraídos
        if vales:
            print("\n📄 EJEMPLO DE VALE PROCESADO:")
            primer_vale = list(vales.values())[0]
            for campo, valor in primer_vale.items():
                if campo not in ['archivo_original', 'ruta_completa']:
                    print(f"   {campo}: {valor}")
        
        if ordenes:
            print("\n📄 EJEMPLO DE ORDEN PROCESADA:")
            primera_orden = list(ordenes.values())[0]
            for campo, valor in primera_orden.items():
                if campo not in ['archivo_original', 'ruta_completa']:
                    print(f"   {campo}: {valor}")
        
        # Obtener estadísticas completas
        stats = autocarga.obtener_estadisticas()
        print(f"\n📈 ESTADÍSTICAS COMPLETAS:")
        for clave, valor in stats.items():
            if isinstance(valor, dict):
                print(f"   {clave}:")
                for subclave, subvalor in valor.items():
                    print(f"      {subclave}: {subvalor}")
            else:
                print(f"   {clave}: {valor}")
        
        # Obtener proveedores para actualizar
        actualizaciones = autocarga.obtener_proveedores_para_actualizar()
        if actualizaciones:
            print(f"\n🔄 PROVEEDORES PARA ACTUALIZAR ({len(actualizaciones)}):")
            for act in actualizaciones:
                print(f"   • {act['nombre']} -> Código: {act['codigo_propuesto']}")
        
        # Guardar resultados
        print(f"\n💾 Guardando resultados...")
        ruta_vales, ruta_ordenes = autocarga.guardar_resultados(".")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extractor_individual():
    """
    Prueba individual de un extractor.
    """
    print("\n🔧 PRUEBA DE EXTRACTOR INDIVIDUAL")
    print("=" * 50)
    
    # Buscar un archivo de prueba
    ruta_test = r"C:\QuiterWeb\cache"
    if os.path.exists(ruta_test):
        archivos = [f for f in os.listdir(ruta_test) if f.endswith('.pdf')]
        
        if archivos:
            archivo_prueba = os.path.join(ruta_test, archivos[0])
            print(f"📄 Probando con: {archivos[0]}")
            
            from extractor import PDFDataExtractor
            extractor = PDFDataExtractor()
            
            try:
                datos = extractor.extract_all_data(archivo_prueba)
                print("✅ Extracción exitosa:")
                for campo, valor in datos.items():
                    print(f"   {campo}: {valor}")
                return True
                
            except Exception as e:
                print(f"❌ Error en extracción: {e}")
                return False
        else:
            print("❌ No se encontraron archivos PDF de prueba")
            return False
    else:
        print(f"❌ Carpeta de prueba no existe: {ruta_test}")
        return False


def test_provider_matcher():
    """
    Prueba individual del matcher de proveedores.
    """
    print("\n🔍 PRUEBA DEL MATCHER DE PROVEEDORES")
    print("=" * 50)
    
    matcher = ProviderMatcher()
    
    # Datos de prueba
    datos_prueba = [
        {'Nombre': 'SERVICIOSGLOBALESELYT', 'Cuenta': '60309'},
        {'Nombre': 'CYBERPUERTASADECV', 'Cuenta': '12345'},
        {'Nombre': 'EMPRESA TEST SA DE CV', 'Cuenta': '99999'}
    ]
    
    for i, datos in enumerate(datos_prueba, 1):
        print(f"\n🧪 Prueba {i}: {datos['Nombre']}")
        proveedor, actualizado = matcher.match_provider_from_vale_data(datos)
        
        if proveedor:
            print(f"   ✅ Proveedor encontrado: {proveedor.nombre}")
            print(f"   🔄 Código actualizado: {actualizado}")
        else:
            print(f"   ❌ Proveedor no encontrado")


if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA AUTOCARGA")
    print("=" * 70)
    
    # Ejecutar pruebas
    success = test_autocarga_completa()
    
    if not success:
        print("\n⚠️ La prueba completa falló, ejecutando pruebas individuales...")
        test_extractor_individual()
        test_provider_matcher()
    
    print("\n🏁 PRUEBAS COMPLETADAS")
