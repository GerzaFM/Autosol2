"""
ButtonsList - Panel de botones de acciones principales
======================================================

Marco que contiene los botones principales para operaciones CRUD y funciones
especiales sobre los proveedores. Proporciona acceso directo a todas las
acciones disponibles en la aplicación.

Botones incluidos:
- Agregar: Crear nuevo proveedor
- Editar: Modificar proveedor seleccionado  
- Eliminar: Borrar proveedor seleccionado
- Combinar: Fusionar proveedores duplicados

Características:
- Layout horizontal optimizado
- Colores semánticos para diferentes acciones
- Ancho consistente para apariencia profesional
- Orden lógico de operaciones (de menos a más destructivo)

Patrones implementados:
- Command Pattern: Cada botón representa una acción/comando
- Semantic UI: Colores que comunican el tipo de acción
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

class ButtonsList:
    """
    Panel de botones para operaciones principales de proveedores.
    
    Organiza las acciones disponibles en un layout horizontal intuitivo,
    con colores semánticos que comunican el propósito de cada operación.
    
    Orden de botones (izquierda a derecha):
    [Combinar] [Eliminar] [Editar] [Agregar]
    
    Colores semánticos:
    - Verde (SUCCESS): Operaciones de creación/confirmación  
    - Amarillo (WARNING): Operaciones de modificación
    - Rojo (DANGER): Operaciones destructivas
    - Azul (INFO): Operaciones especiales/utilidades
    
    Responsabilidades:
    - Proporcionar acceso visual a todas las operaciones CRUD
    - Mantener consistencia visual entre botones
    - Facilitar integración con sistema de eventos del controlador
    - Organizar acciones por frecuencia de uso y seguridad
    
    Integración:
    - Los botones son accesibles como self.button_[nombre]
    - El controlador vincula eventos a cada botón
    - Estados habilitado/deshabilitado controlados externamente
    """
    
    def __init__(self, master):
        """
        Inicializa el panel de botones con todas las acciones principales.
        
        Args:
            master: Widget padre que contendrá este panel
            
        Crea:
        - Marco principal del panel
        - Todos los botones de acción
        - Layout horizontal consistente
        - Configuración de colores semánticos
        """
        self.master = master
        
        # Marco principal del panel de botones
        # Posicionado en la parte superior, ocupando todo el ancho
        # Padding para separación visual de otros componentes
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=X, anchor=N, padx=30, pady=(0, 10))

        # Ancho estándar para todos los botones (consistencia visual)
        button_width = 12

        # === BOTONES DE ACCIÓN (orden de derecha a izquierda en pack) ===
        
        # AGREGAR - Acción más común y segura (verde)
        # Posicionado en el extremo derecho (posición prominente)
        self.button_add = tb.Button(
            self.frame, 
            text="Agregar",               # Texto descriptivo
            bootstyle="success",          # Verde - acción positiva/creación
            width=button_width            # Ancho consistente
        )
        self.button_add.pack(side=RIGHT, padx=(5, 0))

        # EDITAR - Modificación de datos existentes (amarillo/warning)
        # Segunda posición desde la derecha
        self.button_edit = tb.Button(
            self.frame,
            text="Editar",                # Texto descriptivo
            bootstyle="warning",          # Amarillo - acción de modificación
            width=button_width            # Ancho consistente
        )
        self.button_edit.pack(side=RIGHT, padx=(5, 0))

        # ELIMINAR - Acción destructiva (rojo)
        # Tercera posición - separado de agregar/editar para evitar clicks accidentales
        self.button_delete = tb.Button(
            self.frame,
            text="Eliminar",              # Texto descriptivo
            bootstyle="danger",           # Rojo - acción destructiva
            width=button_width            # Ancho consistente
        )
        self.button_delete.pack(side=RIGHT, padx=(5, 0))

        # COMBINAR - Función especial/utilidad (azul)
        # Posición izquierda - función menos común, especializada
        self.button_combine = tb.Button(
            self.frame,
            text="Combinar",              # Texto descriptivo
            bootstyle="info",             # Azul - función especial/informativa
            width=button_width            # Ancho consistente
        )
        self.button_combine.pack(side=RIGHT, padx=(5, 0))
        
        # Nota: El orden de pack es RIGHT, por lo que los botones aparecen
        # en orden inverso: [Combinar] [Eliminar] [Editar] [Agregar]