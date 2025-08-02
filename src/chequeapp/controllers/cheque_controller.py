"""
Controlador principal para la gestión de cheques
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import traceback

# Importar modelos locales
from ..models.cheque_models import ChequeData, ChequeFilters, ChequeState

# Importar base de datos si está disponible
try:
    import sys
    import os
    bd_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bd')
    sys.path.insert(0, bd_path)
    from models import Factura, Proveedor
    from bd_control import DBManager
    DB_AVAILABLE = True
except ImportError as e:
    Factura = Proveedor = DBManager = None
    DB_AVAILABLE = False


class ChequeController:
    """Controlador para gestión de cheques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = ChequeState()
        
        if DB_AVAILABLE:
            self.db_manager = DBManager()
        else:
            self.db_manager = None
            self.logger.warning("Base de datos no disponible")
        
        # Datos de ejemplo para desarrollo
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Carga datos de ejemplo para desarrollo"""
        sample_cheques = [
            ChequeData(
                id=1,
                numero_cheque="001234",
                fecha_cheque=date(2024, 1, 15),
                monto=Decimal('5000.00'),
                beneficiario="Proveedor ABC S.A. de C.V.",
                concepto="Pago de servicios enero 2024",
                banco="BBVA Bancomer",
                cuenta="0123456789",
                estado="COBRADO",
                fecha_cobro=date(2024, 1, 16),
                folio_interno="FAC-2024-001"
            ),
            ChequeData(
                id=2,
                numero_cheque="001235",
                fecha_cheque=date(2024, 2, 10),
                monto=Decimal('3500.50'),
                beneficiario="Servicios XYZ S.C.",
                concepto="Mantenimiento febrero 2024",
                banco="Banamex",
                cuenta="9876543210",
                estado="PENDIENTE",
                folio_interno="FAC-2024-002"
            ),
            ChequeData(
                id=3,
                numero_cheque="001236",
                fecha_cheque=date(2024, 2, 20),
                monto=Decimal('7200.75'),
                beneficiario="Materiales DEF Ltda.",
                concepto="Compra de materiales",
                banco="Santander",
                cuenta="5555666677",
                estado="CANCELADO",
                observaciones="Cheque cancelado por error en monto",
                folio_interno="FAC-2024-003"
            ),
            ChequeData(
                id=4,
                numero_cheque="001237",
                fecha_cheque=date(2024, 3, 5),
                monto=Decimal('12000.00'),
                beneficiario="Constructora GHI S.A.",
                concepto="Pago parcial obra marzo",
                banco="Banorte",
                cuenta="1111222233",
                estado="PENDIENTE",
                folio_interno="FAC-2024-004"
            ),
            ChequeData(
                id=5,
                numero_cheque="001238",
                fecha_cheque=date(2024, 3, 15),
                monto=Decimal('2800.25'),
                beneficiario="Papelería JKL",
                concepto="Suministros de oficina",
                banco="HSBC",
                cuenta="4444555566",
                estado="COBRADO",
                fecha_cobro=date(2024, 3, 16),
                folio_interno="FAC-2024-005"
            )
        ]
        
        self.state.all_cheques = sample_cheques
        self.state.filtered_cheques = sample_cheques.copy()
        self.logger.info(f"Cargados {len(sample_cheques)} cheques de ejemplo")
    
    def get_state(self) -> ChequeState:
        """Obtiene el estado actual"""
        return self.state
    
    def load_cheques(self) -> bool:
        """Carga cheques desde la base de datos"""
        try:
            if not DB_AVAILABLE or not self.db_manager:
                self.logger.warning("Usando datos de ejemplo - DB no disponible")
                return True
            
            # TODO: Implementar carga desde BD real cuando esté disponible
            # Por ahora usar datos de ejemplo
            self.logger.info("Cheques cargados correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando cheques: {e}")
            return False
    
    def apply_filters(self, filters_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aplica filtros a los cheques
        
        Args:
            filters_dict: Diccionario con los filtros
            
        Returns:
            Lista de cheques filtrados como diccionarios
        """
        try:
            filtered_cheques = self.state.all_cheques.copy()
            
            # Filtro por número de cheque
            numero_cheque = filters_dict.get('numero_cheque', '').strip()
            if numero_cheque:
                filtered_cheques = [
                    c for c in filtered_cheques 
                    if numero_cheque.lower() in c.numero_cheque.lower()
                ]
            
            # Filtro por beneficiario
            beneficiario = filters_dict.get('beneficiario', '').strip()
            if beneficiario:
                filtered_cheques = [
                    c for c in filtered_cheques 
                    if beneficiario.lower() in c.beneficiario.lower()
                ]
            
            # Filtro por banco
            banco = filters_dict.get('banco', '').strip()
            if banco:
                filtered_cheques = [
                    c for c in filtered_cheques 
                    if banco.lower() in c.banco.lower()
                ]
            
            # Filtro por estado
            estado = filters_dict.get('estado', '').strip()
            if estado:
                filtered_cheques = [
                    c for c in filtered_cheques 
                    if c.estado == estado
                ]
            
            # Filtro por fecha inicial
            fecha_inicial_str = filters_dict.get('fecha_inicial', '').strip()
            if fecha_inicial_str:
                try:
                    fecha_inicial = datetime.strptime(fecha_inicial_str, '%Y-%m-%d').date()
                    filtered_cheques = [
                        c for c in filtered_cheques 
                        if c.fecha_cheque and c.fecha_cheque >= fecha_inicial
                    ]
                except ValueError:
                    self.logger.warning(f"Formato de fecha inicial inválido: {fecha_inicial_str}")
            
            # Filtro por fecha final
            fecha_final_str = filters_dict.get('fecha_final', '').strip()
            if fecha_final_str:
                try:
                    fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()
                    filtered_cheques = [
                        c for c in filtered_cheques 
                        if c.fecha_cheque and c.fecha_cheque <= fecha_final
                    ]
                except ValueError:
                    self.logger.warning(f"Formato de fecha final inválido: {fecha_final_str}")
            
            # Filtro por monto mínimo
            monto_minimo_str = filters_dict.get('monto_minimo', '').strip()
            if monto_minimo_str:
                try:
                    monto_minimo = Decimal(monto_minimo_str)
                    filtered_cheques = [
                        c for c in filtered_cheques 
                        if c.monto >= monto_minimo
                    ]
                except (ValueError, InvalidOperation):
                    self.logger.warning(f"Monto mínimo inválido: {monto_minimo_str}")
            
            # Filtro por monto máximo
            monto_maximo_str = filters_dict.get('monto_maximo', '').strip()
            if monto_maximo_str:
                try:
                    monto_maximo = Decimal(monto_maximo_str)
                    filtered_cheques = [
                        c for c in filtered_cheques 
                        if c.monto <= monto_maximo
                    ]
                except (ValueError, InvalidOperation):
                    self.logger.warning(f"Monto máximo inválido: {monto_maximo_str}")
            
            # Actualizar estado
            self.state.filtered_cheques = filtered_cheques
            
            # Convertir a diccionarios para la tabla
            results = [cheque.to_dict() for cheque in filtered_cheques]
            
            self.logger.info(f"Filtros aplicados: {len(results)} cheques encontrados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error aplicando filtros: {e}")
            self.logger.error(traceback.format_exc())
            return []
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        self.state.filtered_cheques = self.state.all_cheques.copy()
    
    def get_cheque_by_id(self, cheque_id: int) -> Optional[ChequeData]:
        """Obtiene un cheque por su ID"""
        for cheque in self.state.all_cheques:
            if cheque.id == cheque_id:
                return cheque
        return None
    
    def create_cheque(self, cheque_data: ChequeData) -> bool:
        """Crea un nuevo cheque"""
        try:
            # Asignar ID automático
            max_id = max([c.id for c in self.state.all_cheques if c.id], default=0)
            cheque_data.id = max_id + 1
            
            # Agregar a la lista
            self.state.all_cheques.append(cheque_data)
            self.state.filtered_cheques.append(cheque_data)
            
            self.logger.info(f"Cheque creado: {cheque_data.numero_cheque}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando cheque: {e}")
            return False
    
    def update_cheque(self, cheque_data: ChequeData) -> bool:
        """Actualiza un cheque existente"""
        try:
            for i, cheque in enumerate(self.state.all_cheques):
                if cheque.id == cheque_data.id:
                    self.state.all_cheques[i] = cheque_data
                    break
            
            # Actualizar también en filtered_cheques si existe
            for i, cheque in enumerate(self.state.filtered_cheques):
                if cheque.id == cheque_data.id:
                    self.state.filtered_cheques[i] = cheque_data
                    break
            
            self.logger.info(f"Cheque actualizado: {cheque_data.numero_cheque}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando cheque: {e}")
            return False
    
    def delete_cheque(self, cheque_id: int) -> bool:
        """Elimina un cheque"""
        try:
            # Eliminar de all_cheques
            self.state.all_cheques = [
                c for c in self.state.all_cheques if c.id != cheque_id
            ]
            
            # Eliminar de filtered_cheques
            self.state.filtered_cheques = [
                c for c in self.state.filtered_cheques if c.id != cheque_id
            ]
            
            self.logger.info(f"Cheque eliminado: ID {cheque_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando cheque: {e}")
            return False
    
    def change_cheque_status(self, cheque_id: int, new_status: str) -> bool:
        """Cambia el estado de un cheque"""
        try:
            cheque = self.get_cheque_by_id(cheque_id)
            if not cheque:
                self.logger.warning(f"Cheque no encontrado: ID {cheque_id}")
                return False
            
            old_status = cheque.estado
            cheque.estado = new_status
            
            # Si se marca como cobrado, agregar fecha de cobro
            if new_status == "COBRADO" and not cheque.fecha_cobro:
                cheque.fecha_cobro = date.today()
            
            self.logger.info(f"Estado de cheque cambiado: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cambiando estado del cheque: {e}")
            return False
