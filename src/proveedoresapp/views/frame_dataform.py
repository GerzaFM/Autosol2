"""
DataForm - Formulario de captura y edición de datos
===================================================

Marco que contiene el formulario completo para capturar y editar información
de proveedores. Implementa un layout organizado con todos los campos necesarios
y botones de acción.

Características:
- Layout en dos filas para optimización del espacio
- Campos con SearchBar para mejor experiencia de usuario
- Validación visual en tiempo real
- Estados editables/readonly controlados externamente  
- Botones contextuales (Guardar/Cancelar)

Campos incluidos:
- Código Quiter, Nombre Fiscal, Email, Nombre Contacto
- RFC, Nombre en Quiter, Teléfono
- Todos con placeholders descriptivos

Patrones implementados:
- Composite Pattern: Agrupación de controles relacionados
- State Pattern: Estados de edición controlados externamente
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Importar componente personalizado con manejo de errores
try:
    from proveedoresapp.views.searchbar import SearchBar
except ImportError:
    # Fallback para ejecución independiente o casos de error de importación
    from searchbar import SearchBar
finally:
    # Fallback de seguridad si SearchBar no está disponible
    if SearchBar is None:
        class SearchBar:
            """Fallback SearchBar básico para casos de emergencia."""
            def __init__(self, master, placeholder="", width=100):
                self.entry = tb.Entry(master, bootstyle=PRIMARY, width=width)
                self.entry.insert(0, placeholder)
                self.entry.pack(side=LEFT, fill=X, padx=5, pady=5)


class DataForm:
    """
    Formulario completo para captura y edición de datos de proveedores.
    
    Organiza todos los campos necesarios en un layout eficiente de dos filas,
    con botones de acción en la parte inferior.
    
    Layout de campos:
    Fila 1: [Código] [Nombre Fiscal] [Email] [Nombre Contacto]
    Fila 2: [RFC] [Nombre Quiter] [Teléfono]
    Botones: [Cancelar] [Guardar]
    
    Responsabilidades:
    - Proporcionar interfaz de captura para todos los campos de proveedor
    - Mantener referencias a todos los controles para acceso externo
    - Ofrecer botones contextuales para operaciones CRUD
    - Soportar estados de edición (habilitado/deshabilitado)
    
    Integración:
    - Los campos son accesibles como self.entry_[nombre_campo]
    - Los botones son accesibles como self.button_[accion]
    - El controlador maneja los eventos y estados
    """
    
    def __init__(self, master):
        """
        Inicializa el formulario con todos sus componentes.
        
        Args:
            master: Widget padre que contendrá este formulario
            
        Crea:
        - Marco principal del formulario
        - Todos los campos de entrada
        - Botones de acción
        - Layout organizado en filas
        """
        self.master = master
        
        # Marco principal del formulario
        # Posicionado en la parte superior sin expansión para mantener compacto
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, anchor=N, pady=(30, 10), expand=False)

        # Referencias a botones (inicializadas después)
        self.button_cancelar = None
        self.button_guardar = None

        # Crear la estructura del formulario
        self.create_form()
        self.create_buttons()

    def create_form(self):
        """
        Crea la estructura del formulario con campos organizados en filas.
        
        Layout organizado:
        - frame_top: Primera fila de campos principales
        - frame_middle: Segunda fila de campos complementarios  
        - frame_bottom: Será usado para botones (creado en create_buttons)
        
        Organización de campos por relevancia y flujo de captura:
        - Fila 1: Identificación y contacto principal
        - Fila 2: Identificación fiscal y contacto secundario
        """
        
        # === MARCOS DE ORGANIZACIÓN ===
        
        # Primera fila de campos
        frame_top = tb.Frame(self.frame)
        frame_top.pack(side=TOP, fill=X, padx=15, pady=5)

        # Segunda fila de campos  
        frame_midle = tb.Frame(self.frame)
        frame_midle.pack(side=TOP, fill=X, padx=15, pady=5)

        # Reservar espacio para botones (usado en create_buttons)
        frame_bottom = tb.Frame(self.frame)
        frame_bottom.pack(side=TOP, fill=X, padx=15, pady=5)

        # === DEFINICIÓN DE TAMAÑOS ===
        
        # Tamaños estándar para diferentes tipos de campos
        small = 15    # Campos cortos: códigos, RFC
        medium = 30   # Campos medianos: teléfono, email
        large = 50    # Campos largos: nombres completos

        # === PRIMERA FILA DE CAMPOS ===
        
        # Código Quiter - Identificador numérico en sistema externo
        self.entry_codigo = SearchBar(
            frame_top, 
            placeholder="Codigo quiter",  # Texto de ayuda
            width=small                   # Tamaño compacto para números
        )
        
        # Nombre fiscal completo - Campo principal de identificación
        self.entry_nombre = SearchBar(
            frame_top,
            placeholder="Nombre fiscal",  # Nombre oficial/legal
            width=large                   # Espacio amplio para nombres largos
        )
        
        # Email de contacto - Comunicación electrónica
        self.entry_email = SearchBar(
            frame_top,
            placeholder="Email",          # Correo electrónico
            width=medium                  # Tamaño estándar para emails
        )
        
        # Nombre de persona de contacto - Responsable/enlace
        self.entry_nombre_contacto = SearchBar(
            frame_top,
            placeholder="Nombre contacto", # Persona responsable
            width=medium                   # Espacio medio para nombres
        )

        # === SEGUNDA FILA DE CAMPOS ===

        # RFC - Registro Federal de Contribuyentes (México)
        self.entry_rfc = SearchBar(
            frame_midle,
            placeholder="RFC",            # Identificación fiscal
            width=small                   # 12-13 caracteres máximo
        )
        
        # Nombre como aparece en sistema Quiter - Puede diferir del oficial
        self.entry_nombre_quiter = SearchBar(
            frame_midle,
            placeholder="Nombre quiter",  # Nombre en sistema externo
            width=large                   # Espacio amplio
        )
        
        # Teléfono de contacto - Comunicación directa
        self.entry_telefono = SearchBar(
            frame_midle,
            placeholder="Telefono",       # Número telefónico
            width=medium                  # Espacio estándar
        )

        # === EMPAQUETADO DE CONTROLES ===
        
        # Primera fila - de izquierda a derecha
        self.entry_codigo.pack(side=LEFT, fill=X, padx=5, pady=5)
        self.entry_nombre.pack(side=LEFT, fill=X, padx=5, pady=5)   
        self.entry_email.pack(side=LEFT, fill=X, padx=5, pady=5) 
        self.entry_nombre_contacto.pack(side=LEFT, fill=X, padx=5, pady=5)

        # Segunda fila - de izquierda a derecha
        self.entry_rfc.pack(side=LEFT, fill=X, padx=5, pady=5)       
        self.entry_nombre_quiter.pack(side=LEFT, fill=X, padx=5, pady=5)
        self.entry_telefono.pack(side=LEFT, fill=X, padx=5, pady=5)

    def create_buttons(self):
        """
        Crea los botones de acción del formulario.
        
        Botones incluidos:
        - Guardar: Confirma operación (crear/actualizar)
        - Cancelar: Cancela operación y limpia formulario
        
        Layout: Alineados a la derecha con orden visual lógico
        [Cancelar] [Guardar] (Cancelar a la izquierda, Guardar a la derecha)
        
        Estilos:
        - Guardar: SUCCESS (verde) - acción positiva
        - Cancelar: DANGER (rojo) - acción de cancelación
        """
        
        # Marco para contener los botones
        frame_bottom = tb.Frame(self.frame)
        frame_bottom.pack(side=TOP, fill=X, padx=15, pady=5)

        # Botón Guardar - Acción principal
        # Posicionado a la derecha (más prominente)
        self.button_guardar = tb.Button(
            frame_bottom, 
            text="Guardar",               # Texto descriptivo
            bootstyle=SUCCESS,            # Color verde (acción positiva)
            width=12                      # Ancho fijo para consistencia
        )
        self.button_guardar.pack(side=RIGHT, padx=(5, 15), pady=(0, 5))

        # Botón Cancelar - Acción secundaria  
        # Posicionado a la izquierda del botón Guardar
        self.button_cancelar = tb.Button(
            frame_bottom,
            text="Cancelar",              # Texto descriptivo
            bootstyle=DANGER,             # Color rojo (acción de cancelación)
            width=12                      # Ancho fijo para consistencia
        )
        self.button_cancelar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))


# === CÓDIGO DE PRUEBA INDEPENDIENTE ===

if __name__ == "__main__":
    """
    Código de prueba para ejecutar el formulario de manera independiente.
    
    Útil para:
    - Desarrollo y testing del componente
    - Verificación visual del layout
    - Pruebas de funcionalidad aislada
    
    Uso: python frame_dataform.py
    """
    import tkinter as tk
    import ttkbootstrap as tb

    # Crear ventana de prueba
    root = tb.Window(themename="flatly")
    root.title("Prueba DataForm")

    # Instanciar y mostrar el formulario
    app = DataForm(root)
    
    # Iniciar bucle de eventos
    root.mainloop()


