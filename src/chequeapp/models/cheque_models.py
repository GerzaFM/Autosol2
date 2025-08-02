"""
Modelos de datos específicos para la aplicación de Cheques
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import date, datetime
from dataclasses import dataclass


@dataclass
class ChequeData:
    """Modelo de datos para un cheque"""
    id: Optional[int] = None
    numero_cheque: str = ""
    fecha_cheque: Optional[date] = None
    monto: Decimal = Decimal('0.00')
    beneficiario: str = ""
    concepto: str = ""
    banco: str = ""
    cuenta: str = ""
    estado: str = "PENDIENTE"  # PENDIENTE, COBRADO, CANCELADO
    fecha_cobro: Optional[date] = None
    observaciones: str = ""
    
    # Relación con factura
    factura_id: Optional[int] = None
    folio_interno: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'numero_cheque': self.numero_cheque,
            'fecha_cheque': self.fecha_cheque.isoformat() if self.fecha_cheque else '',
            'monto': str(self.monto),
            'beneficiario': self.beneficiario,
            'concepto': self.concepto,
            'banco': self.banco,
            'cuenta': self.cuenta,
            'estado': self.estado,
            'fecha_cobro': self.fecha_cobro.isoformat() if self.fecha_cobro else '',
            'observaciones': self.observaciones,
            'factura_id': self.factura_id,
            'folio_interno': self.folio_interno
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChequeData':
        """Crea un objeto desde un diccionario"""
        instance = cls()
        instance.id = data.get('id')
        instance.numero_cheque = data.get('numero_cheque', '')
        
        # Manejar fechas
        fecha_cheque_str = data.get('fecha_cheque', '')
        if fecha_cheque_str:
            if isinstance(fecha_cheque_str, str):
                instance.fecha_cheque = datetime.strptime(fecha_cheque_str, '%Y-%m-%d').date()
            else:
                instance.fecha_cheque = fecha_cheque_str
        
        fecha_cobro_str = data.get('fecha_cobro', '')
        if fecha_cobro_str:
            if isinstance(fecha_cobro_str, str):
                instance.fecha_cobro = datetime.strptime(fecha_cobro_str, '%Y-%m-%d').date()
            else:
                instance.fecha_cobro = fecha_cobro_str
        
        # Manejar monto
        monto_str = data.get('monto', '0.00')
        if isinstance(monto_str, str):
            instance.monto = Decimal(monto_str)
        else:
            instance.monto = Decimal(str(monto_str))
        
        instance.beneficiario = data.get('beneficiario', '')
        instance.concepto = data.get('concepto', '')
        instance.banco = data.get('banco', '')
        instance.cuenta = data.get('cuenta', '')
        instance.estado = data.get('estado', 'PENDIENTE')
        instance.observaciones = data.get('observaciones', '')
        instance.factura_id = data.get('factura_id')
        instance.folio_interno = data.get('folio_interno', '')
        
        return instance


@dataclass
class ChequeFilters:
    """Filtros para búsqueda de cheques"""
    fecha_inicial: str = ''
    fecha_final: str = ''
    numero_cheque: str = ''
    beneficiario: str = ''
    banco: str = ''
    estado: str = ''
    monto_minimo: Optional[Decimal] = None
    monto_maximo: Optional[Decimal] = None
    
    def has_active_filters(self) -> bool:
        """Verifica si hay filtros activos"""
        return bool(
            self.fecha_inicial or self.fecha_final or self.numero_cheque or
            self.beneficiario or self.banco or self.estado or
            self.monto_minimo is not None or self.monto_maximo is not None
        )


@dataclass
class ChequeState:
    """Estado de la aplicación de cheques"""
    all_cheques: List[ChequeData] = None
    filtered_cheques: List[ChequeData] = None
    selected_cheque: Optional[ChequeData] = None
    bancos_data: List[str] = None
    estados_data: List[str] = None
    
    def __post_init__(self):
        if self.all_cheques is None:
            self.all_cheques = []
        if self.filtered_cheques is None:
            self.filtered_cheques = []
        if self.bancos_data is None:
            self.bancos_data = [
                "BBVA Bancomer",
                "Banamex",
                "Santander",
                "Banorte",
                "HSBC",
                "Scotiabank",
                "Inbursa",
                "Azteca",
                "BanBajío",
                "Otro"
            ]
        if self.estados_data is None:
            self.estados_data = ["PENDIENTE", "COBRADO", "CANCELADO"]
