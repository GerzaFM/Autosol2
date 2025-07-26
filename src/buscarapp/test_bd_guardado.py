#!/usr/bin/env python3
"""
Script para probar el guardado de vales en BD
"""
import sys
import os
sys.path.insert(0, '..')

from autocarga.autocarga import AutoCarga
from controllers.autocarga_controller import AutocargaController
from bd.models import Vale, Proveedor, Factura
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_autocarga_con_bd():
    print("=== PROBANDO AUTOCARGA CON GUARDADO EN BD ===")
    
    try:
        # Ejecutar AutoCarga directamente
        autocarga = AutoCarga(
            ruta_carpeta='C:/QuiterWeb/cache', 
            dias_atras=7
        )
        
        vales, ordenes = autocarga.ejecutar_autocarga()
        stats = autocarga.obtener_estadisticas()
        
        print(f"\n📊 Vales encontrados: {len(vales)}")
        print(f"📊 Órdenes encontradas: {len(ordenes)}")
        
        if len(vales) > 0:
            print(f"\n🔄 Intentando guardar vales en BD...")
            
            # Procesar cada vale individualmente
            vales_guardados = 0
            errores = 0
            
            for vale_id, vale_data in list(vales.items())[:3]:  # Solo los primeros 3 para prueba
                try:
                    print(f"\n📄 Procesando vale: {vale_id}")
                    print(f"   Número: {vale_data.get('numero', 'N/A')}")
                    print(f"   Proveedor: {vale_data.get('nombre', 'N/A')}")
                    print(f"   Total: {vale_data.get('total', 'N/A')}")
                    
                    # Verificar si ya existe
                    numero_vale = vale_data.get('numero', '')
                    if numero_vale:
                        try:
                            vale_existente = Vale.get(Vale.noVale == numero_vale)
                            print(f"   ⚠️ Vale ya existe en BD: {numero_vale}")
                            continue
                        except Vale.DoesNotExist:
                            pass
                    
                    # Preparar datos para BD
                    datos_vale = {
                        'noVale': numero_vale,
                        'tipo': vale_data.get('tipo_de_vale', ''),
                        'noDocumento': vale_data.get('no_documento', ''),
                        'descripcion': vale_data.get('descripcion', ''),
                        'referencia': int(vale_data.get('referencia', 0)) if vale_data.get('referencia') else 0,
                        'total': str(vale_data.get('total', '')),
                        'cuenta': int(vale_data.get('cuenta', 0)) if vale_data.get('cuenta') else None,
                        'fechaVale': vale_data.get('fecha'),
                        'departamento': None,  # Estos los podemos mapear después
                        'sucursal': None,
                        'marca': None,
                        'responsable': None,
                        'proveedor': vale_data.get('nombre', '')
                    }
                    
                    # Crear vale en BD
                    nuevo_vale = Vale.create(**datos_vale)
                    print(f"   ✅ Vale guardado exitosamente con ID: {nuevo_vale.id}")
                    vales_guardados += 1
                    
                except Exception as e:
                    print(f"   ❌ Error guardando vale: {e}")
                    errores += 1
            
            print(f"\n📊 RESUMEN:")
            print(f"   ✅ Vales guardados: {vales_guardados}")
            print(f"   ❌ Errores: {errores}")
            
            # Verificar que se guardaron en BD
            print(f"\n🔍 VERIFICANDO EN BD:")
            total_vales_bd = Vale.select().count()
            print(f"   📊 Total vales en BD ahora: {total_vales_bd}")
            
            # Mostrar vales de NAVA MEDRANO
            vales_nava = Vale.select().where(
                (Vale.proveedor.contains('NAVA')) | 
                (Vale.proveedor.contains('MEDRANO'))
            )
            
            print(f"\n🏢 VALES DE SERVICIO NAVA MEDRANO EN BD:")
            for vale in vales_nava:
                print(f"   📄 {vale.noVale} - {vale.proveedor} - ${vale.total}")
        
        else:
            print("❌ No se encontraron vales para procesar")
    
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_autocarga_con_bd()
