"""
AutoCarga - Sistema Unificado de Extracción de PDFs
====================================================
Clase principal que combina todas las funcionalidades para:
- Buscar archivos Vales (QRSVCMX) y Órdenes (QRSOPMX208)
- Extraer datos automáticamente
- Crear diccionarios separados para cada tipo de documento
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Importar nuestros extractores
from .extractor import PDFDataExtractor
from .extractor_orden import OrdenDataExtractor
from .lector_carpeta import buscar_vales_y_ordenes_recientes
from .provider_matcher import ProviderMatcher


class AutoCarga:
    """
    Clase principal que unifica la búsqueda y extracción de datos de PDFs.
    Maneja tanto Vales (QRSVCMX) como Órdenes (QRSOPMX208).
    """
    
    def __init__(self, ruta_carpeta: str = r"C:\QuiterWeb\cache", dias_atras: int = 2):
        """
        Inicializa el sistema de autocarga.
        
        Args:
            ruta_carpeta (str): Ruta donde buscar los archivos PDF
            dias_atras (int): Cuántos días atrás buscar archivos (default: 2)
        """
        self.ruta_carpeta = ruta_carpeta
        self.dias_atras = dias_atras
        
        # Inicializar extractores
        self.extractor_vales = PDFDataExtractor()
        self.extractor_ordenes = OrdenDataExtractor()
        
        # Inicializar matcher de proveedores
        self.provider_matcher = ProviderMatcher()
        
        # Diccionarios de resultados
        self.vales = {}
        self.ordenes = {}
        
        # Estadísticas
        self.stats = {
            'vales_encontrados': 0,
            'ordenes_encontradas': 0,
            'vales_procesados': 0,
            'ordenes_procesadas': 0,
            'vales_exitosos': 0,
            'ordenes_exitosas': 0,
            'errores_vales': 0,
            'errores_ordenes': 0,
            'timestamp': None
        }
    
    def buscar_archivos(self) -> Tuple[List[str], List[str]]:
        """
        Busca archivos Vales y Órdenes en la carpeta especificada.
        
        Returns:
            Tuple[List[str], List[str]]: (lista_vales, lista_ordenes)
        """
        # logging.info(f"🔍 Buscando archivos en: {self.ruta_carpeta}")
        # logging.info(f"📅 Archivos modificados en los últimos {self.dias_atras} días")
        # logging.info("-" * 60)
        
        try:
            tupla_vales, tupla_ordenes = buscar_vales_y_ordenes_recientes(
                ruta_carpeta=self.ruta_carpeta,
                dias=self.dias_atras
            )
            
            # Convertir tuplas a listas
            lista_vales = list(tupla_vales)
            lista_ordenes = list(tupla_ordenes)
            
            self.stats['vales_encontrados'] = len(lista_vales)
            self.stats['ordenes_encontradas'] = len(lista_ordenes)
            
            # logging.info(f"💳 Vales encontrados: {len(lista_vales)}")
            # logging.info(f"📋 Órdenes encontradas: {len(lista_ordenes)}")
            # logging.info("-" * 60)
            
            return lista_vales, lista_ordenes
            
        except Exception as e:
            print(f"❌ Error al buscar archivos: {e}")
            return [], []
    
    def procesar_vales(self, lista_vales: List[str]) -> Dict[str, Any]:
        """
        Procesa todos los archivos de Vales y crea el diccionario correspondiente.
        
        Args:
            lista_vales (List[str]): Lista de rutas de archivos de Vales
            
        Returns:
            Dict[str, Any]: Diccionario con datos de Vales procesados
        """
        # logging.info("🚀 PROCESANDO VALES")
        # logging.info("=" * 40)
        
        vales_dict = {}
        procesados = 0
        exitosos = 0
        errores = 0
        
        for i, archivo_vale in enumerate(lista_vales, 1):
            try:
                nombre_archivo = Path(archivo_vale).name
                # logging.info(f"📄 {i}/{len(lista_vales)} Procesando: {nombre_archivo}")
                
                # Extraer datos del Vale
                datos = self.extractor_vales.extract_all_data(archivo_vale)
                
                if datos and any(datos.values()):
                    # Crear clave única basada en el nombre del archivo
                    clave = Path(archivo_vale).stem
                    vales_dict[clave] = datos
                    exitosos += 1
                    # logging.info(f"   ✅ Datos extraídos exitosamente")
                    # logging.info(f"   🔢 Número: {datos.get('Numero', 'N/A')}")
                    # logging.info(f"   🏢 Nombre: {datos.get('Nombre', 'N/A')}")
                    # logging.info(f"   💰 Total: {datos.get('Total', 'N/A')}")
                    # logging.info(f"   📝 Descripción: {datos.get('Descripcion', 'N/A')}")
                else:
                    errores += 1
                    # logging.info(f"   ❌ No se pudieron extraer datos")
                
                procesados += 1
                
            except Exception as e:
                errores += 1
                # logging.info(f"   ❌ Error al procesar: {str(e)}")
        
        # Actualizar estadísticas
        self.stats['vales_procesados'] = procesados
        self.stats['vales_exitosos'] = exitosos
        self.stats['errores_vales'] = errores
        
        # logging.info("\n" + "=" * 40)
        # logging.info(f"📊 RESUMEN VALES: {exitosos}/{procesados} exitosos")
        # logging.info("=" * 40)
        
        return vales_dict
    
    def procesar_ordenes(self, lista_ordenes: List[str]) -> Dict[str, Any]:
        """
        Procesa todos los archivos de Órdenes y crea el diccionario correspondiente.
        
        Args:
            lista_ordenes (List[str]): Lista de rutas de archivos de Órdenes
            
        Returns:
            Dict[str, Any]: Diccionario con datos de Órdenes procesadas
        """
        # logging.info("🚀 PROCESANDO ÓRDENES")
        # logging.info("=" * 40)
        
        ordenes_dict = {}
        procesados = 0
        exitosos = 0
        errores = 0
        
        for i, archivo_orden in enumerate(lista_ordenes, 1):
            try:
                nombre_archivo = Path(archivo_orden).name
                # logging.info(f"📄 {i}/{len(lista_ordenes)} Procesando: {nombre_archivo}")
                
                # Extraer datos de la Orden
                datos = self.extractor_ordenes.extract_all_data(archivo_orden)
                
                if datos and any(datos.values()):
                    # Crear clave única basada en el nombre del archivo
                    clave = Path(archivo_orden).stem
                    ordenes_dict[clave] = datos
                    exitosos += 1
                    # logging.info(f"   ✅ Datos extraídos exitosamente")
                    # logging.info(f"   📋 Ref. Movimiento: {datos.get('Ref_Movimiento', 'N/A')}")
                    # logging.info(f"   🏢 Nombre: {datos.get('Nombre', 'N/A')}")
                    # logging.info(f"   💰 Importe: {datos.get('Importe', 'N/A')}")
                    # logging.info(f"   🏛️ Banco: {datos.get('Codigo_Banco', 'N/A')}")
                else:
                    errores += 1
                    # logging.info(f"   ❌ No se pudieron extraer datos")
                
                procesados += 1
                
            except Exception as e:
                errores += 1
                # logging.info(f"   ❌ Error al procesar: {str(e)}")
        
        # Actualizar estadísticas
        self.stats['ordenes_procesadas'] = procesados
        self.stats['ordenes_exitosas'] = exitosos
        self.stats['errores_ordenes'] = errores
        
        print("\n" + "=" * 40)
        print(f"📊 RESUMEN ÓRDENES: {exitosos}/{procesados} exitosos")
        print("=" * 40)
        
        return ordenes_dict
    
    def ejecutar_autocarga(self, progress_callback=None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Ejecuta el proceso completo de autocarga.
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: (diccionario_vales, diccionario_ordenes)
        """
        print("🚀 SISTEMA DE AUTOCARGA - INICIO")
        print("=" * 60)
        
        # Registrar timestamp
        self.stats['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Buscar archivos
        lista_vales, lista_ordenes = self.buscar_archivos()

        total_archivos = len(lista_vales) + len(lista_ordenes)
        idx = 0

        # 2. Procesar Vales
        if lista_vales:
            vales_dict = {}
            for i, archivo_vale in enumerate(lista_vales, 1):
                try:
                    nombre_archivo = Path(archivo_vale).name
                    print(f"📄 {i}/{len(lista_vales)} Procesando: {nombre_archivo}")
                    datos = self.extractor_vales.extract_all_data(archivo_vale)
                    if datos and any(datos.values()):
                        clave = Path(archivo_vale).stem
                        vales_dict[clave] = datos
                        print(f"   ✅ Datos extraídos exitosamente")
                    else:
                        print(f"   ❌ No se pudieron extraer datos")
                except Exception as e:
                    print(f"   ❌ Error al procesar: {str(e)}")
                idx += 1
                if progress_callback:
                    progress_callback(idx, total_archivos)
            self.vales = vales_dict
        else:
            print("💳 No se encontraron Vales para procesar")

        print()  # Línea en blanco

        # 3. Procesar Órdenes
        if lista_ordenes:
            ordenes_dict = {}
            for i, archivo_orden in enumerate(lista_ordenes, 1):
                try:
                    nombre_archivo = Path(archivo_orden).name
                    print(f"📄 {i}/{len(lista_ordenes)} Procesando: {nombre_archivo}")
                    datos = self.extractor_ordenes.extract_all_data(archivo_orden)
                    if datos and any(datos.values()):
                        clave = Path(archivo_orden).stem
                        ordenes_dict[clave] = datos
                        print(f"   ✅ Datos extraídos exitosamente")
                    else:
                        print(f"   ❌ No se pudieron extraer datos")
                except Exception as e:
                    print(f"   ❌ Error al procesar: {str(e)}")
                idx += 1
                if progress_callback:
                    progress_callback(idx, total_archivos)
            self.ordenes = ordenes_dict
        else:
            print("📋 No se encontraron Órdenes para procesar")

        # 4. Solo guardar estadísticas sin mostrar reportes adicionales
        # self.mostrar_resumen_final()  # Comentado para evitar reportes duplicados

        # 5. Solo obtener estadísticas sin mostrar reportes en consola
        # self.provider_matcher.print_matching_report(self.vales, self.ordenes)  # Comentado para evitar reportes duplicados

        return self.vales, self.ordenes
    
    def mostrar_resumen_final(self):
        """
        Muestra un resumen completo del procesamiento.
        """
        print("\n" + "🎯 RESUMEN FINAL DEL PROCESAMIENTO")
        print("=" * 60)
        print(f"📅 Timestamp: {self.stats['timestamp']}")
        print(f"📂 Carpeta: {self.ruta_carpeta}")
        print(f"⏱️ Período: Últimos {self.dias_atras} días")
        print("-" * 60)
        print(f"💳 VALES:")
        print(f"   📁 Encontrados: {self.stats['vales_encontrados']}")
        print(f"   🔄 Procesados: {self.stats['vales_procesados']}")
        print(f"   ✅ Exitosos: {self.stats['vales_exitosos']}")
        print(f"   ❌ Errores: {self.stats['errores_vales']}")
        if self.stats['vales_procesados'] > 0:
            tasa_vales = (self.stats['vales_exitosos'] / self.stats['vales_procesados']) * 100
            print(f"   📊 Tasa de éxito: {tasa_vales:.1f}%")
        print("-" * 60)
        print(f"📋 ÓRDENES:")
        print(f"   📁 Encontradas: {self.stats['ordenes_encontradas']}")
        print(f"   🔄 Procesadas: {self.stats['ordenes_procesadas']}")
        print(f"   ✅ Exitosas: {self.stats['ordenes_exitosas']}")
        print(f"   ❌ Errores: {self.stats['errores_ordenes']}")
        if self.stats['ordenes_procesadas'] > 0:
            tasa_ordenes = (self.stats['ordenes_exitosas'] / self.stats['ordenes_procesadas']) * 100
            print(f"   📊 Tasa de éxito: {tasa_ordenes:.1f}%")
        print("=" * 60)
    
    def guardar_resultados(self, carpeta_destino: str = None) -> Tuple[str, str]:
        """
        Guarda los diccionarios de resultados en archivos JSON.
        
        Args:
            carpeta_destino (str): Carpeta donde guardar (default: carpeta actual)
            
        Returns:
            Tuple[str, str]: (ruta_archivo_vales, ruta_archivo_ordenes)
        """
        if carpeta_destino is None:
            carpeta_destino = "."
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Preparar datos para guardar
        datos_vales = {
            'metadata': {
                'timestamp': self.stats['timestamp'],
                'total_vales': len(self.vales),
                'carpeta_origen': self.ruta_carpeta,
                'dias_atras': self.dias_atras
            },
            'vales': self.vales
        }
        
        datos_ordenes = {
            'metadata': {
                'timestamp': self.stats['timestamp'],
                'total_ordenes': len(self.ordenes),
                'carpeta_origen': self.ruta_carpeta,
                'dias_atras': self.dias_atras
            },
            'ordenes': self.ordenes
        }
        
        # Guardar archivos
        ruta_vales = os.path.join(carpeta_destino, f"vales_autocarga_{timestamp}.json")
        ruta_ordenes = os.path.join(carpeta_destino, f"ordenes_autocarga_{timestamp}.json")
        
        try:
            with open(ruta_vales, 'w', encoding='utf-8') as f:
                json.dump(datos_vales, f, indent=2, ensure_ascii=False)
            
            with open(ruta_ordenes, 'w', encoding='utf-8') as f:
                json.dump(datos_ordenes, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Archivos guardados:")
            print(f"   📄 Vales: {ruta_vales}")
            print(f"   📄 Órdenes: {ruta_ordenes}")
            
            return ruta_vales, ruta_ordenes
            
        except Exception as e:
            print(f"❌ Error al guardar archivos: {e}")
            return "", ""
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas del procesamiento.
        
        Returns:
            Dict[str, Any]: Diccionario con estadísticas completas
        """
        stats = self.stats.copy()
        
        # Agregar estadísticas de coincidencias de proveedores
        if hasattr(self, 'provider_matcher'):
            matching_stats = self.provider_matcher.get_matching_stats(self.vales, self.ordenes)
            stats['provider_matching'] = matching_stats
        
        return stats
    
    def obtener_proveedores_para_actualizar(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de proveedores que pueden ser actualizados con códigos QuiteR.
        
        Returns:
            List[Dict]: Lista de proveedores con datos para actualizar
        """
        actualizaciones = []
        
        for vale_id, vale_data in self.vales.items():
            nombre = vale_data.get('Nombre', '').strip()
            cuenta = vale_data.get('Cuenta', '').strip()
            
            if nombre and cuenta:
                # Buscar si existe el proveedor sin código
                proveedor = self.provider_matcher.find_provider_by_name(nombre)
                if proveedor and not proveedor.codigo_quiter:
                    actualizaciones.append({
                        'proveedor_id': proveedor.id,
                        'nombre': proveedor.nombre,
                        'codigo_propuesto': cuenta,
                        'fuente': f'Vale {vale_id}'
                    })
        
        return actualizaciones