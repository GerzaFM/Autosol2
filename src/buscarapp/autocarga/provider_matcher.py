"""
Utilidad para comparar y actualizar proveedores basado en datos extraídos de PDFs.
Maneja la lógica de:
- Comparar nombres sin espacios
- Usar el campo "Cuenta" como codigo_quiter
- Actualizar proveedores existentes con códigos faltantes
"""

import sys
import os
from typing import Dict, Optional, List, Tuple
import logging

# Agregar path para imports de la base de datos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from bd.models import Proveedor
except ImportError:
    # Fallback si no se puede importar
    print("⚠️ No se pudo importar el modelo Proveedor")
    Proveedor = None


class ProviderMatcher:
    """
    Clase para manejar la lógica de comparación y actualización de proveedores
    basado en datos extraídos de PDFs de vales y órdenes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def normalize_name(self, name: str) -> str:
        """
        Normaliza un nombre para comparación quitando espacios y caracteres especiales.
        
        Args:
            name (str): Nombre a normalizar
            
        Returns:
            str: Nombre normalizado sin espacios ni caracteres especiales
        """
        if not name:
            return ""
        
        # Convertir a mayúsculas y quitar espacios
        normalized = name.upper().replace(" ", "")
        
        # Quitar caracteres especiales comunes
        normalized = normalized.replace(".", "").replace(",", "").replace("-", "")
        normalized = normalized.replace("&", "").replace("/", "").replace("\\", "")
        
        # Normalizar abreviaciones comunes de empresas
        # SA DE CV -> SADECV
        normalized = normalized.replace("SADECV", "SADECV")
        normalized = normalized.replace("SADERL", "SADERL") 
        normalized = normalized.replace("SDERL", "SDERL")
        normalized = normalized.replace("SCDERL", "SCDERL")
        
        # Quitar palabras comunes que pueden aparecer de diferentes formas
        normalized = normalized.replace("SOCIEDAD", "")
        normalized = normalized.replace("ANONIMA", "")
        normalized = normalized.replace("CAPITAL", "")
        normalized = normalized.replace("VARIABLE", "")
        normalized = normalized.replace("RESPONSABILIDAD", "")
        normalized = normalized.replace("LIMITADA", "")
        
        return normalized
    
    def find_provider_by_code(self, codigo_quiter: str) -> Optional[object]:
        """
        Busca un proveedor por su código QuiteR.
        
        Args:
            codigo_quiter (str): Código QuiteR del proveedor
            
        Returns:
            Optional[Proveedor]: Proveedor encontrado o None
        """
        if not Proveedor or not codigo_quiter:
            return None
        
        try:
            return Proveedor.get(Proveedor.codigo_quiter == codigo_quiter)
        except Proveedor.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error buscando proveedor por código {codigo_quiter}: {e}")
            return None
    
    def find_provider_by_name(self, name: str) -> Optional[object]:
        """
        Busca un proveedor por nombre usando comparación sin espacios.
        
        Args:
            name (str): Nombre del proveedor a buscar
            
        Returns:
            Optional[Proveedor]: Proveedor encontrado o None
        """
        if not Proveedor or not name:
            return None
        
        normalized_target = self.normalize_name(name)
        
        try:
            # Obtener todos los proveedores y comparar nombres normalizados
            proveedores = Proveedor.select()
            
            for proveedor in proveedores:
                normalized_db = self.normalize_name(proveedor.nombre)
                
                # Comparación exacta
                if normalized_db == normalized_target:
                    return proveedor
                
                # Comparación parcial - el nombre del PDF puede incluir "SADECV" extra
                if normalized_target.endswith('SADECV'):
                    # Quitar "SADECV" del final y comparar
                    target_sin_sadecv = normalized_target[:-6]  # Quitar "SADECV"
                    if normalized_db == target_sin_sadecv:
                        return proveedor
                
                # Comparación inversa - el nombre de BD puede ser más completo
                if normalized_db.endswith('SADECV'):
                    db_sin_sadecv = normalized_db[:-6]
                    if db_sin_sadecv == normalized_target:
                        return proveedor
                
                # Comparación por contención - uno contiene al otro
                if len(normalized_target) > 10 and len(normalized_db) > 10:
                    if normalized_target in normalized_db or normalized_db in normalized_target:
                        # Verificar que la coincidencia sea significativa (>80% del nombre más corto)
                        min_len = min(len(normalized_target), len(normalized_db))
                        max_len = max(len(normalized_target), len(normalized_db))
                        if min_len / max_len > 0.8:
                            return proveedor
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error buscando proveedor por nombre {name}: {e}")
            return None
    
    def update_provider_code(self, proveedor: object, codigo_quiter: str) -> bool:
        """
        Actualiza el código QuiteR de un proveedor existente.
        
        Args:
            proveedor: Instancia del proveedor
            codigo_quiter (str): Nuevo código QuiteR
            
        Returns:
            bool: True si se actualizó correctamente
        """
        if not proveedor or not codigo_quiter:
            return False
        
        try:
            proveedor.codigo_quiter = codigo_quiter
            proveedor.save()
            self.logger.info(f"Código QuiteR '{codigo_quiter}' asignado al proveedor '{proveedor.nombre}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando código del proveedor: {e}")
            return False
    
    def match_provider_from_vale_data(self, vale_data: Dict) -> Tuple[Optional[object], bool]:
        """
        Encuentra o actualiza un proveedor basado en datos de un vale.
        
        Args:
            vale_data (Dict): Datos extraídos del vale (debe contener 'Nombre' y 'Cuenta')
            
        Returns:
            Tuple[Optional[Proveedor], bool]: (proveedor_encontrado, fue_actualizado)
        """
        nombre = vale_data.get('Nombre', '').strip()
        cuenta = vale_data.get('Cuenta', '').strip()
        
        if not nombre and not cuenta:
            return None, False
        
        proveedor = None
        fue_actualizado = False
        
        # 1. Si hay cuenta, buscar por código QuiteR primero
        if cuenta:
            proveedor = self.find_provider_by_code(cuenta)
            
            # Si no se encuentra por código pero hay nombre, buscar por nombre
            if not proveedor and nombre:
                proveedor = self.find_provider_by_name(nombre)
                
                # Si se encuentra por nombre, actualizar su código
                if proveedor and not proveedor.codigo_quiter:
                    fue_actualizado = self.update_provider_code(proveedor, cuenta)
        
        # 2. Si no hay cuenta o no se encontró, buscar solo por nombre
        elif nombre:
            proveedor = self.find_provider_by_name(nombre)
        
        return proveedor, fue_actualizado
    
    def match_provider_from_orden_data(self, orden_data: Dict) -> Optional[object]:
        """
        Encuentra un proveedor basado en datos de una orden.
        
        Args:
            orden_data (Dict): Datos extraídos de la orden (debe contener 'Nombre')
            
        Returns:
            Optional[Proveedor]: Proveedor encontrado o None
        """
        nombre = orden_data.get('Nombre', '').strip()
        
        if not nombre:
            return None
        
        # Para órdenes, solo buscar por nombre (no tienen código QuiteR)
        return self.find_provider_by_name(nombre)
    
    def get_matching_stats(self, vales_data: Dict, ordenes_data: Dict) -> Dict:
        """
        Obtiene estadísticas de coincidencias de proveedores.
        
        Args:
            vales_data (Dict): Datos de vales procesados
            ordenes_data (Dict): Datos de órdenes procesadas
            
        Returns:
            Dict: Estadísticas de coincidencias
        """
        stats = {
            'vales_con_proveedor': 0,
            'vales_sin_proveedor': 0,
            'ordenes_con_proveedor': 0,
            'ordenes_sin_proveedor': 0,
            'proveedores_actualizados': 0,
            'nombres_no_encontrados': []
        }
        
        # Procesar vales
        for vale_id, vale_data in vales_data.items():
            proveedor, fue_actualizado = self.match_provider_from_vale_data(vale_data)
            
            if proveedor:
                stats['vales_con_proveedor'] += 1
                if fue_actualizado:
                    stats['proveedores_actualizados'] += 1
            else:
                stats['vales_sin_proveedor'] += 1
                nombre = vale_data.get('Nombre', 'Sin nombre')
                if nombre not in stats['nombres_no_encontrados']:
                    stats['nombres_no_encontrados'].append(nombre)
        
        # Procesar órdenes
        for orden_id, orden_data in ordenes_data.items():
            proveedor = self.match_provider_from_orden_data(orden_data)
            
            if proveedor:
                stats['ordenes_con_proveedor'] += 1
            else:
                stats['ordenes_sin_proveedor'] += 1
                nombre = orden_data.get('Nombre', 'Sin nombre')
                if nombre not in stats['nombres_no_encontrados']:
                    stats['nombres_no_encontrados'].append(nombre)
        
        return stats
    
    def print_matching_report(self, vales_data: Dict, ordenes_data: Dict):
        """
        Imprime un reporte de coincidencias de proveedores.
        
        Args:
            vales_data (Dict): Datos de vales procesados
            ordenes_data (Dict): Datos de órdenes procesadas
        """
        stats = self.get_matching_stats(vales_data, ordenes_data)
        
        print("\n" + "🔍 REPORTE DE COINCIDENCIAS DE PROVEEDORES")
        print("=" * 60)
        print(f"💳 VALES:")
        print(f"   ✅ Con proveedor encontrado: {stats['vales_con_proveedor']}")
        print(f"   ❌ Sin proveedor: {stats['vales_sin_proveedor']}")
        print(f"📋 ÓRDENES:")
        print(f"   ✅ Con proveedor encontrado: {stats['ordenes_con_proveedor']}")
        print(f"   ❌ Sin proveedor: {stats['ordenes_sin_proveedor']}")
        print(f"🔄 Proveedores actualizados con nuevo código: {stats['proveedores_actualizados']}")
        
        if stats['nombres_no_encontrados']:
            print(f"\n⚠️ NOMBRES NO ENCONTRADOS EN BD:")
            for nombre in stats['nombres_no_encontrados']:
                print(f"   • {nombre}")
        
        print("=" * 60)


def test_matcher():
    """
    Función de prueba para el matcher de proveedores.
    """
    matcher = ProviderMatcher()
    
    # Datos de prueba
    vale_test = {
        'Nombre': 'SERVICIOS GLOBALES ELYT',
        'Cuenta': '60309'
    }
    
    orden_test = {
        'Nombre': 'CYBERPUERTASADECV'
    }
    
    print("🧪 PRUEBA DEL MATCHER DE PROVEEDORES")
    print("=" * 50)
    
    # Probar vale
    proveedor, actualizado = matcher.match_provider_from_vale_data(vale_test)
    print(f"Vale - Proveedor encontrado: {proveedor.nombre if proveedor else 'No encontrado'}")
    print(f"Vale - Código actualizado: {actualizado}")
    
    # Probar orden
    proveedor_orden = matcher.match_provider_from_orden_data(orden_test)
    print(f"Orden - Proveedor encontrado: {proveedor_orden.nombre if proveedor_orden else 'No encontrado'}")


if __name__ == "__main__":
    test_matcher()
