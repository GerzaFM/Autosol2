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
        Inicializa la barra lateral.
        
        Args:
            parent: Widget padre
            width_expanded: Ancho cuando está expandida
            width_collapsed: Ancho cuando está colapsada
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger(__name__)
        self.width_expanded = width_expanded
        self.width_collapsed = width_collapsed
        self.is_expanded = True
        
        # Lista de botones (btn, icon, text, callback)
        self.menu_buttons: List[Tuple[tb.Button, str, str, Optional[Callable]]] = []
        
        # Configurar el frame
        self.config(width=self.width_expanded, bootstyle="dark")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets base de la barra lateral."""
        # Botón de colapsar/expandir
        self.toggle_button = tb.Button(
            self,
            text="≡",
            width=3,
            bootstyle="secondary",
            command=self.toggle
        )
        self.toggle_button.pack(side=TOP, padx=5, pady=10, anchor='w')
        
        # Frame para botones superiores
        self.top_frame = tb.Frame(self, bootstyle="dark")
        self.top_frame.pack(side=TOP, fill="x", padx=5, pady=2)
        
        # Espaciador
        self.spacer = tb.Label(self, text="", bootstyle="dark")
        self.spacer.pack(side=TOP, fill="both", expand=True)
        
        # Frame para botones inferiores
        self.bottom_frame = tb.Frame(self, bootstyle="dark")
        self.bottom_frame.pack(side=BOTTOM, fill="x", padx=5, pady=2)
    
    def add_menu_item(self, text: str, icon: str, callback: Optional[Callable] = None, 
                     position: str = "top") -> tb.Button:
        """
        Agrega un elemento al menú.
        
        Args:
            text: Texto del botón
            icon: Icono del botón
            callback: Función a ejecutar al hacer clic
            position: "top" o "bottom"
            
        Returns:
            El botón creado
        """
        parent_frame = self.top_frame if position == "top" else self.bottom_frame
        
        btn = tb.Button(
            parent_frame,
            text=f"{icon}   {text}",  # Sin formato de relleno
            bootstyle="dark",
            command=callback
        )
        
        if position == "top":
            btn.pack(side=TOP, pady=2, anchor='w')  # Sin fill="x"
        else:
            btn.pack(side=BOTTOM, pady=2, anchor='w')

        # Agregar efectos hover
        self._bind_hover_effects(btn)
        
        # Guardar referencia
        self.menu_buttons.append((btn, icon, text, callback))
        
        self.logger.debug(f"Elemento de menú agregado: {text}")
        return btn
    
    def _bind_hover_effects(self, button: tb.Button):
        """
        Agrega efectos de hover a un botón.
        
        Args:
            button: Botón al que agregar efectos
        """
        def on_enter(event):
            button.config(bootstyle="success")
        
        def on_leave(event):
            button.config(bootstyle="dark")
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def toggle(self):
        """Alterna entre expandido y colapsado."""
        self.is_expanded = not self.is_expanded
        self._update_state()
    
    def expand(self):
        """Expande la barra lateral."""
        if not self.is_expanded:
            self.is_expanded = True
            self._update_state()
    
    def collapse(self):
        """Colapsa la barra lateral."""
        if self.is_expanded:
            self.is_expanded = False
            self._update_state()
    
    def _update_state(self):
        """Actualiza el estado visual de la barra lateral."""
        try:
            if self.is_expanded:
                self.config(width=self.width_expanded)
                # Mostrar texto completo en botones
                for btn, icon, text, _ in self.menu_buttons:
                    btn.config(text=f"{icon}   {text}")
            else:
                self.config(width=self.width_collapsed)
                # Mostrar solo iconos
                for btn, icon, text, _ in self.menu_buttons:
                    btn.config(text=icon)
            
            # Forzar actualización
            self.update_idletasks()
            
        except Exception as e:
            self.logger.error(f"Error al actualizar estado de barra lateral: {e}")
    
    def set_active_item(self, text: str):
        """
        Marca un elemento como activo.
        
        Args:
            text: Texto del elemento a marcar como activo
        """
        for btn, icon, btn_text, _ in self.menu_buttons:
            if btn_text == text:
                btn.config(bootstyle="primary")
            else:
                btn.config(bootstyle="dark")
    
    def clear_active(self):
        """Limpia la selección activa."""
        for btn, _, _, _ in self.menu_buttons:
            btn.config(bootstyle="dark")
