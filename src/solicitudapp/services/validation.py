"""
Servicio de validación para la aplicación.
"""
import re
from decimal import Decimal, InvalidOperation
from typing import List, Tuple


class ValidationService:
    """Servicio centralizado para validaciones."""
    
    @staticmethod
    def validar_rfc(rfc: str) -> Tuple[bool, str]:
        """Valida formato de RFC mexicano."""
        rfc = rfc.strip().upper()
        # Patrón básico para RFC (persona física o moral)
        patron_pf = r'^[A-Z]{4}[0-9]{6}[A-Z0-9]{3}$'  # Persona física
        patron_pm = r'^[A-Z]{3}[0-9]{6}[A-Z0-9]{3}$'  # Persona moral
        
        if re.match(patron_pf, rfc) or re.match(patron_pm, rfc):
            return True, ""
        return False, "Formato de RFC inválido"
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """Valida formato de email."""
        if not email.strip():
            return True, ""  # Email es opcional
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(patron, email):
            return True, ""
        return False, "Formato de email inválido"
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """Valida formato de teléfono."""
        if not telefono.strip():
            return True, ""  # Teléfono es opcional
        
        # Eliminar espacios, guiones y paréntesis
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        
        if re.match(r'^\d{10}$', telefono_limpio):
            return True, ""
        return False, "El teléfono debe tener 10 dígitos"
    
    @staticmethod
    def validar_numero(valor: str, campo: str) -> Tuple[bool, str]:
        """Valida que un valor sea un número válido."""
        if not valor.strip():
            return False, f"El campo {campo} es obligatorio"
        
        try:
            numero = Decimal(valor)
            if numero < 0:
                return False, f"El campo {campo} no puede ser negativo"
            return True, ""
        except InvalidOperation:
            return False, f"El campo {campo} debe ser un número válido"
    
    @staticmethod
    def validar_campos_obligatorios(datos: dict, campos_obligatorios: List[str]) -> List[str]:
        """Valida que los campos obligatorios no estén vacíos."""
        errores = []
        for campo in campos_obligatorios:
            valor = datos.get(campo, "")
            if not str(valor).strip():
                errores.append(f"El campo {campo} es obligatorio")
        return errores
    
    @staticmethod
    def validar_suma_categorias(valores: List[str]) -> Tuple[bool, str]:
        """
        Valida que la suma de los valores numéricos de categorías sea exactamente 100.
        :param valores: Lista de strings con los valores de las categorías.
        :return: (bool, mensaje de error si aplica)
        """
        try:
            suma = 0
            for valor in valores:
                if valor.strip():
                    suma += float(valor)
            if suma != 100:
                return False, "La suma de las categorías debe ser exactamente 100"
            return True, ""
        except ValueError:
            return False, "Todos los valores de categorías deben ser numéricos"


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
