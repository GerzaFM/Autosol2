"""
Lector de carpeta para buscar archivos de Vales y Órdenes recientes.
Busca archivos PDF con patrones específicos modificados en los últimos días.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, List


def buscar_vales_y_ordenes_recientes(ruta_carpeta: str, dias: int = 2) -> Tuple[List[str], List[str]]:
    """
    Busca archivos de Vales y Órdenes modificados en los últimos días.
    
    Args:
        ruta_carpeta (str): Ruta de la carpeta donde buscar
        dias (int): Número de días atrás para buscar (default: 2)
        
    Returns:
        Tuple[List[str], List[str]]: (lista_vales, lista_ordenes)
    """
    # Patrones para identificar archivos
    patron_vales = "QRSVCMX"  # Vales
    patron_ordenes = "QRSOPMX208"  # Órdenes
    
    # Calcular fecha límite
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    vales = []
    ordenes = []
    
    try:
        # Verificar que la carpeta existe
        if not os.path.exists(ruta_carpeta):
            print(f"❌ La carpeta {ruta_carpeta} no existe")
            return vales, ordenes
        
        # Buscar archivos en la carpeta
        for archivo in os.listdir(ruta_carpeta):
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            
            # Solo procesar archivos PDF
            if not archivo.lower().endswith('.pdf'):
                continue
            
            # Verificar fecha de modificación
            try:
                fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                if fecha_modificacion < fecha_limite:
                    continue
            except OSError:
                continue
            
            # Clasificar por tipo de archivo
            if patron_vales in archivo:
                vales.append(ruta_completa)
            elif patron_ordenes in archivo:
                ordenes.append(ruta_completa)
        
        # Ordenar por fecha de modificación (más recientes primero)
        vales.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        ordenes.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
    except Exception as e:
        print(f"❌ Error al buscar archivos: {e}")
    
    return vales, ordenes


def listar_archivos_disponibles(ruta_carpeta: str, patron: str = "") -> List[str]:
    """
    Lista todos los archivos PDF disponibles en la carpeta.
    
    Args:
        ruta_carpeta (str): Ruta de la carpeta
        patron (str): Patrón opcional para filtrar archivos
        
    Returns:
        List[str]: Lista de archivos encontrados
    """
    archivos = []
    
    try:
        if not os.path.exists(ruta_carpeta):
            return archivos
        
        for archivo in os.listdir(ruta_carpeta):
            if archivo.lower().endswith('.pdf'):
                if not patron or patron in archivo:
                    ruta_completa = os.path.join(ruta_carpeta, archivo)
                    archivos.append(ruta_completa)
        
        archivos.sort()
        
    except Exception as e:
        print(f"❌ Error al listar archivos: {e}")
    
    return archivos


def test_lector():
    """
    Función de prueba para el lector de carpetas.
    """
    ruta_test = r"C:\QuiterWeb\cache"
    
    print("🧪 PRUEBA DEL LECTOR DE CARPETAS")
    print("=" * 50)
    print(f"📂 Carpeta: {ruta_test}")
    print(f"📅 Buscando archivos de los últimos 2 días")
    print()
    
    vales, ordenes = buscar_vales_y_ordenes_recientes(ruta_test, 2)
    
    print(f"💳 Vales encontrados: {len(vales)}")
    for vale in vales[:5]:  # Mostrar solo los primeros 5
        print(f"   📄 {Path(vale).name}")
    if len(vales) > 5:
        print(f"   ... y {len(vales) - 5} más")
    
    print(f"\n📋 Órdenes encontradas: {len(ordenes)}")
    for orden in ordenes[:5]:  # Mostrar solo las primeras 5
        print(f"   📄 {Path(orden).name}")
    if len(ordenes) > 5:
        print(f"   ... y {len(ordenes) - 5} más")


if __name__ == "__main__":
    test_lector()
