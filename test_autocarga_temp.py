#!/usr/bin/env python3
"""
Script temporal para probar AutoCarga
"""
import sys
import os
sys.path.insert(0, 'src')

from src.buscarapp.autocarga.autocarga import AutoCarga
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_autocarga():
    print("=== INICIANDO PRUEBA DE AUTOCARGA ===")
    
    # Crear instancia de AutoCarga
    autocarga = AutoCarga(
        ruta_carpeta='C:/QuiterWeb/cache', 
        dias_atras=1  # Solo archivos de hoy
    )
    
    # Ejecutar autocarga
    print("Ejecutando autocarga...")
    vales, ordenes = autocarga.ejecutar_autocarga()
    
    # Obtener estadísticas
    stats = autocarga.obtener_estadisticas()
    
    print(f"\n=== ESTADÍSTICAS ===")
    print(f"Archivos encontrados: {stats.get('archivos_encontrados', 0)}")
    print(f"Vales procesados exitosamente: {stats.get('vales_exitosos', 0)}")
    print(f"Vales con errores: {stats.get('vales_errores', 0)}")
    print(f"Órdenes procesadas exitosamente: {stats.get('ordenes_exitosas', 0)}")
    print(f"Órdenes con errores: {stats.get('ordenes_errores', 0)}")
    
    print(f"\n=== PRIMEROS 3 VALES ENCONTRADOS ===")
    for i, (id_vale, datos) in enumerate(list(vales.items())[:3]):
        print(f"Vale {i+1}: {id_vale}")
        print(f"  Nombre: {datos.get('nombre', 'No encontrado')}")
        print(f"  Número: {datos.get('numero', 'No encontrado')}")
        print(f"  Fecha: {datos.get('fecha', 'No encontrado')}")
        print(f"  Total: {datos.get('total', 'No encontrado')}")
        print("---")
    
    # Buscar específicamente "SERVICIO NAVA MEDRANO"
    print(f"\n=== BUSCANDO 'SERVICIO NAVA MEDRANO' ===")
    encontrado = False
    for id_vale, datos in vales.items():
        nombre = datos.get('nombre', '').upper()
        if 'NAVA' in nombre or 'MEDRANO' in nombre or 'SERVICIO' in nombre:
            print(f"ENCONTRADO: {id_vale}")
            print(f"  Nombre completo: {datos.get('nombre', '')}")
            print(f"  Archivo: {datos.get('archivo_origen', '')}")
            encontrado = True
    
    if not encontrado:
        print("No se encontró 'SERVICIO NAVA MEDRANO' en los vales procesados")
        
        # Verificar si hay archivos de hoy
        print(f"\nTotal de vales encontrados hoy: {len(vales)}")
        if len(vales) == 0:
            print("No hay vales de hoy. Probando con más días...")
            # Probar con más días
            autocarga2 = AutoCarga(ruta_carpeta='C:/QuiterWeb/cache', dias_atras=7)
            vales2, ordenes2 = autocarga2.ejecutar_autocarga()
            print(f"Vales encontrados en los últimos 7 días: {len(vales2)}")

if __name__ == "__main__":
    test_autocarga()
