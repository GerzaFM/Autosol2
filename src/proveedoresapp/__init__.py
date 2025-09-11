"""
ProveedoresApp - Sistema de Gestión de Proveedores
=================================================

Módulo principal de la aplicación de proveedores que implementa el patrón MVC
para la gestión completa de proveedores empresariales.

Arquitectura:
- Model: ProveedorModel (gestión de datos y BD)
- View: ProveedoreView (interfaz gráfica)
- Controller: Controller (lógica de negocio y eventos)

Características principales:
- CRUD completo de proveedores
- Búsqueda y filtrado avanzado
- Validaciones robustas
- Interfaz moderna con ttkbootstrap
- Logging completo de operaciones

Autor: Sistema TCM Matehuala
Versión: 0.0.0
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Importar componentes del patrón MVC
from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.controllers.contoller import Controller
from proveedoresapp.models.model import ProveedorModel


class ProveedoresApp(tb.Frame):
    """
    Clase principal de la aplicación de proveedores.
    
    Implementa el punto de entrada y orquestador del patrón MVC.
    Hereda de tb.Frame para integrarse como componente en aplicaciones más grandes.
    
    Responsabilidades:
    - Inicializar los componentes MVC en el orden correcto
    - Establecer la comunicación entre Model, View y Controller
    - Configurar el contenedor principal de la aplicación
    
    Uso:
        root = tb.Window()
        app = ProveedoresApp(root)
        root.mainloop()
    """
    
    def __init__(self, master):
        """
        Inicializa la aplicación de proveedores.
        
        Args:
            master: Widget padre que contendrá esta aplicación
            
        Patrón de inicialización MVC:
        1. Model: Manejo de datos y base de datos
        2. View: Interfaz gráfica y componentes visuales
        3. Controller: Lógica de negocio y coordinación
        """
        super().__init__(master)
        
        # Inicializar componentes MVC en orden de dependencias
        self.model = ProveedorModel()           # Primero: Acceso a datos
        self.view = ProveedoreView(self)        # Segundo: Interfaz gráfica  
        self.controller = Controller(self.model, self.view)  # Tercero: Coordinador
        
        # Configurar este frame para ocupar todo el espacio disponible
        # Permite integración flexible en aplicaciones más grandes
        self.pack(fill='both', expand=True)

