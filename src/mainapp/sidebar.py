"""
Componente de barra lateral (sidebar) reutilizable.
MainApp - Sidebar independiente en src/mainapp/
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Callable, List, Tuple, Optional
import logging

from app.utils.logger import get_logger

class SidebarComponent(tb.Frame):
    """
    Componente de barra lateral expandible/colapsable.
    """
    
    def __init__(self, parent, width_expanded: int = 200, width_collapsed: int = 60, **kwargs):
        """
        Inicializa la navbar horizontal.
        
        Args:
            parent: Widget padre
            width_expanded: No usado (mantenido para compatibilidad)
            width_collapsed: No usado (mantenido para compatibilidad)
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        
        # Lista de botones (btn, icon, text, callback)
        self.menu_buttons: List[Tuple[tb.Button, str, str, Optional[Callable]]] = []
        
        # Control de elemento activo
        self.active_button = None
        
        # Configurar el frame como navbar horizontal
        self.bar_color = "dark"
        self.buton_color = "dark"
        self.selected_color = "secondary"
        self.config(height=50, bootstyle=self.bar_color)  # Altura fija para navbar con fondo gris
        self.pack_propagate(False)  # Mantener altura fija
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets base de la navbar horizontal."""
        # Frame para botones principales (centrados horizontalmente)
        self.top_frame = tb.Frame(self, bootstyle=self.bar_color)
        self.top_frame.pack(side=LEFT, expand=True, padx=0, pady=4)
        
        # Frame para botones secundarios (lado derecho)
        self.bottom_frame = tb.Frame(self, bootstyle=self.bar_color)
        self.bottom_frame.pack(side=RIGHT, padx=0, pady=4)
    
    def add_menu_item(self, text: str, icon: str, callback: Optional[Callable] = None, 
                     position: str = "top") -> tb.Button:
        """
        Agrega un elemento al menú navbar horizontal.
        
        Args:
            text: Texto del botón
            icon: Icono del botón
            callback: Función a ejecutar al hacer clic
            position: "top" (centro) o "bottom" (derecha)
            
        Returns:
            El botón creado
        """
        parent_frame = self.top_frame if position == "top" else self.bottom_frame
        
        btn = tb.Button(
            parent_frame,
            text=f"{icon}   {text}",  # Siempre mostrar icono y texto
            bootstyle=self.buton_color,
            command=callback
        )
        
        # Empaquetado horizontal
        if position == "top":
            btn.pack(side=LEFT, padx=5, pady=2)  # Botones principales en el centro
        else:
            btn.pack(side=RIGHT, padx=5, pady=2)  # Botones secundarios a la derecha

        # Agregar a la lista de referencias (sin efectos hover)
        self.menu_buttons.append((btn, icon, text, callback))
        
        self.logger.debug(f"Elemento de menú agregado: {text}")
        return btn

    def set_active_item(self, button: tb.Button):
        """
        Establece el elemento activo usando un estilo outline más sutil.
        
        Args:
            button: El botón a marcar como activo
        """
        # Restaurar el botón anterior a su estado normal
        if self.active_button:
            try:
                # Restaurar estilo normal
                self.active_button.config(bootstyle=self.buton_color)
            except Exception as e:
                self.logger.debug(f"Error al restaurar estilo normal: {e}")
        
        # Establecer nuevo botón activo
        self.active_button = button
        if button:
            try:
                # Aplicar estilo outline para diferenciación visual sutil
                button.config(bootstyle=self.selected_color)
            except Exception as e:
                self.logger.debug(f"Error al aplicar estilo activo: {e}")
                # Fallback: mantener el botón como está
                pass
