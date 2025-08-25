from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class SearchFilters:
    id: Optional[int] = field(default=None)
    codigo_quiter: Optional[int] = field(default=None)
    nombre: Optional[str] = field(default=None)
    nombre_en_quiter: Optional[str] = field(default=None)
    rfc: Optional[str] = field(default=None)
    telefono: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    nombre_contacto: Optional[str] = field(default=None)
    cuenta_mayor: Optional[int] = field(default=None)
