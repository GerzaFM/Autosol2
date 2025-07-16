"""
Modelos de datos para la aplicación de Solicitud de Compra.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from decimal import Decimal
from datetime import date


@dataclass
class Concepto:
    """Representa un concepto individual en una solicitud."""
    cantidad: Decimal
    descripcion: str
    precio: Decimal
    total: Decimal
    
    def __post_init__(self):
        """Validación automática después de inicialización."""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if abs(self.total - (self.cantidad * self.precio)) > 0.01:
            raise ValueError("El total no coincide con cantidad * precio")


@dataclass
class Proveedor:
    """Representa los datos de un proveedor."""
    nombre: str = ""
    rfc: str = ""
    telefono: str = ""
    correo: str = ""
    contacto: str = ""
    
    def es_valido(self) -> bool:
        """Verifica si los datos mínimos del proveedor están presentes."""
        return bool(self.nombre.strip() and self.rfc.strip())


@dataclass
class Totales:
    """Representa los totales de una solicitud."""
    subtotal: Decimal = field(default_factory=lambda: Decimal('0'))
    retencion: Decimal = field(default_factory=lambda: Decimal('0'))
    iva: Decimal = field(default_factory=lambda: Decimal('0'))
    total: Decimal = field(default_factory=lambda: Decimal('0'))
    
    def calcular_total(self) -> Decimal:
        """Calcula el total basado en subtotal, retención e IVA."""
        return self.subtotal - self.retencion + self.iva


@dataclass
class Solicitud:
    """Representa una solicitud de compra completa."""
    # Datos de la solicitud
    fecha: date = field(default_factory=date.today)
    clase: str = ""
    tipo: str = "Compra"  # "Compra" o "Servicio"
    departamento: str = "Administracion"
    folio: str = ""
    
    # Datos del proveedor
    proveedor: Proveedor = field(default_factory=Proveedor)
    
    # Conceptos y totales
    conceptos: List[Concepto] = field(default_factory=list)
    totales: Totales = field(default_factory=Totales)
    
    # Comentarios
    comentarios: str = ""
    
    def agregar_concepto(self, concepto: Concepto) -> None:
        """Agrega un concepto y recalcula totales."""
        self.conceptos.append(concepto)
        self.recalcular_totales()
    
    def eliminar_concepto(self, indice: int) -> None:
        """Elimina un concepto por índice y recalcula totales."""
        if 0 <= indice < len(self.conceptos):
            del self.conceptos[indice]
            self.recalcular_totales()
    
    def recalcular_totales(self) -> None:
        """Recalcula los totales basándose en los conceptos."""
        subtotal = sum(concepto.total for concepto in self.conceptos)
        self.totales.subtotal = subtotal
        # Mantener retención e IVA existentes, solo actualizar total
        self.totales.total = self.totales.calcular_total()
    
    def es_valida(self) -> tuple[bool, List[str]]:
        """Valida la solicitud y retorna errores si los hay."""
        errores = []
        
        if not self.proveedor.es_valido():
            errores.append("Datos del proveedor incompletos")
        
        if not self.conceptos:
            errores.append("Debe agregar al menos un concepto")
        
        if not self.folio.strip():
            errores.append("El folio es obligatorio")
        
        return len(errores) == 0, errores
