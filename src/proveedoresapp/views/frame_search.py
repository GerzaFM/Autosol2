"""
SearchFrame - Panel de búsqueda y filtros
==========================================

Marco que contiene los controles de búsqueda y filtrado para la lista de proveedores.
Proporciona una interfaz intuitiva para localizar registros específicos.

Componentes incluidos:
- SearchBar: Campo de búsqueda con placeholder inteligente  
- Botón Actualizar: Refresh manual de datos
- Toggle Incompletos: Filtro para proveedores con datos faltantes

Características:
- Búsqueda en tiempo real mientras el usuario escribe
- Filtros combinables para búsquedas específicas
- Layout horizontal optimizado para pantallas estándar
- Integración con el sistema de eventos del controlador
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Importar componente personalizado
from proveedoresapp.views.searchbar import SearchBar

class SearchFrame:
    """
    Marco de controles de búsqueda y filtrado.
    
    Proporciona una interfaz unificada para todas las opciones de búsqueda
    y filtrado disponibles en la aplicación de proveedores.
    
    Layout: [SearchBar] [Actualizar] [☑ Incompletos]
    
    Responsabilidades:
    - Capturar texto de búsqueda del usuario
    - Controlar filtros especializados (incompletos)
    - Proveer botón de actualización manual
    - Exponer interfaces para el controlador
    
    Uso:
        search_frame = SearchFrame(parent)
        texto = search_frame.search_bar.get_search_text()
        incompletos = search_frame.incomplete_var.get()
    """
    
    def __init__(self, master):
        """
        Inicializa el marco de búsqueda con todos sus controles.
        
        Args:
            master: Widget padre que contendrá este marco
            
        Layout creado:
        - Frame principal centrado en la parte superior
        - Frame interno para agrupar controles horizontalmente
        - SearchBar, botón y checkbox alineados horizontalmente
        """
        self.master = master
        
        # Marco principal del componente
        # Ubicado en la parte superior, ocupando todo el ancho disponible
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=X, anchor=N, pady=(30, 10))

        # Marco interno para centrar y agrupar los controles
        # Permite que los controles se mantengan juntos y centrados
        self.inner_frame = tb.Frame(self.frame)
        self.inner_frame.pack()

        # === COMPONENTES DE BÚSQUEDA ===
        
        # Campo de búsqueda principal con placeholder inteligente
        # Ancho de 50 caracteres para acomodar nombres largos de proveedores
        self.search_bar = SearchBar(
            self.inner_frame, 
            "Buscar proveedor...",  # Placeholder descriptivo
            width=50                # Ancho generoso para búsquedas
        )
        # Posicionar a la izquierda con espacio para el siguiente control
        self.search_bar.inner_frame.pack(side=LEFT, padx=(0, 5))

        # Botón de actualización manual
        # Permite refresh de datos sin depender de búsqueda automática
        self.button_search = tb.Button(
            self.inner_frame, 
            text="Actualizar"
        )
        self.button_search.pack(side=LEFT)

        # === CONTROLES DE FILTRADO ===
        
        # Variable para el estado del filtro de incompletos
        # BooleanVar de tkinter para binding automático con checkbox
        self.incomplete_var = tb.BooleanVar()
        
        # Checkbox para filtrar solo proveedores con datos incompletos
        # Estilo "success-round-toggle" para apariencia moderna
        self.switch_incomplete = tb.Checkbutton(
            self.inner_frame, 
            text="Incompletos",                    # Etiqueta descriptiva
            bootstyle="success-round-toggle",      # Estilo visual moderno
            variable=self.incomplete_var           # Variable de estado
        )
        # Posicionar con espacio separado de los controles principales
        self.switch_incomplete.pack(side=LEFT, padx=(15, 0))