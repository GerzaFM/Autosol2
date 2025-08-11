"""
Aplicación de Cheques - Módulo principal
Frame vacío siguiendo arquitectura profesional
"""

try:
    from .cheque_app import ChequeApp
except ImportError:
    ChequeApp = None

try:
    from .cheque_app_professional import ChequeAppProfessional
except ImportError:
    ChequeAppProfessional = None

__version__ = '1.0.0'
__author__ = 'Desarrollo Autosol'
__all__ = ['ChequeApp', 'ChequeAppProfessional']