"""
SearchBar - Componente de búsqueda reutilizable
===============================================

Widget personalizado que extiende tb.Entry con funcionalidad de placeholder
inteligente y adaptación automática a temas.

Características:
- Placeholder que desaparece automáticamente al recibir foco
- Adaptación automática a temas claros/oscuros
- Estados múltiples: normal, readonly, disabled
- Eventos personalizados para integración
- API compatible con Entry estándar

Patrones implementados:
- State Pattern: Para manejo de estados del campo
- Strategy Pattern: Para adaptación de colores por tema
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

class SearchBar:
    """
    Widget de entrada de texto con placeholder inteligente.
    
    Proporciona una experiencia de usuario mejorada con placeholder que
    se oculta automáticamente al recibir foco y manejo inteligente de estados.
    
    Características avanzadas:
    - Auto-detección de tema para colores apropiados
    - Placeholder que desaparece al hacer clic o recibir foco
    - Estados visuales distintos para readonly/disabled
    - API simple compatible con Entry de tkinter
    
    Uso básico:
        search = SearchBar(parent, placeholder="Buscar...", width=30)
        search.pack(side=LEFT, padx=5)
        text = search.get_search_text()
    """
    
    def __init__(self, master, placeholder="Ingrese un texto:", width=10):
        """
        Inicializa el SearchBar con configuración personalizada.
        
        Args:
            master: Widget padre que contendrá este SearchBar
            placeholder (str): Texto de ayuda que se muestra cuando está vacío
            width (int): Ancho del campo en caracteres
        """
        # Contenedor principal para el componente
        self.inner_frame = tb.Frame(master)
        
        # Configuración del componente
        self.entry_search = None
        self.placeholder_text = placeholder
        self.placeholder_active = True  # Estado del placeholder
        self.width = width
        
        # Configurar colores según el tema actual
        self._setup_colors()

        # Crear la interfaz visual
        self.create_widgets()
    
    def _setup_colors(self):
        """
        Configura los colores del componente según el tema actual.
        
        Detecta automáticamente si el tema es claro u oscuro y establece
        los colores apropiados para:
        - Texto del placeholder (gris)
        - Texto normal del usuario
        - Estado deshabilitado
        
        Fallback: Si no puede detectar el tema, usa colores por defecto.
        """
        try:
            # Intentar detectar el tema actual de ttkbootstrap
            style = tb.Style()
            theme_name = style.theme.name if hasattr(style, 'theme') else 'flatly'
            
            # Configurar paleta de colores según el tipo de tema
            if 'dark' in theme_name.lower():
                # Tema oscuro: colores apropiados para fondo oscuro
                self.placeholder_color = "gray"
                self.text_color = "white"
                self.disabled_color = "#555555"  # Gris oscuro para campos deshabilitados
            else:
                # Tema claro: colores apropiados para fondo claro
                self.placeholder_color = "gray"
                self.text_color = "black"
                self.disabled_color = "#999999"  # Gris claro para campos deshabilitados
        except:
            # Fallback seguro si falla la detección de tema
            self.placeholder_color = "gray"
            self.text_color = "black"
            self.disabled_color = "#999999"

    def create_widgets(self):
        """
        Crea y configura los widgets visuales del SearchBar.
        
        Inicializa:
        - Entry principal con configuración personalizada
        - Texto placeholder inicial
        - Event handlers para focus/blur
        - Empaquetado en el contenedor
        """
        # Crear Entry sin placeholdertext nativo - implementamos placeholder manualmente
        self.entry_search = tb.Entry(
            self.inner_frame, 
            font=("Segoe UI", 10),          # Fuente moderna y legible
            foreground=self.placeholder_color,  # Color inicial del placeholder
            width=self.width
        )
        self.entry_search.pack(side=LEFT, padx=10)
        
        # Insertar texto placeholder inicial
        self.entry_search.insert(0, self.placeholder_text)
        
        # Configurar eventos para manejo inteligente del placeholder
        self.entry_search.bind('<FocusIn>', self._on_entry_click)    # Al recibir foco
        self.entry_search.bind('<Button-1>', self._on_entry_click)   # Al hacer clic
        self.entry_search.bind('<FocusOut>', self._on_focus_out)     # Al perder foco
    
    def _on_entry_click(self, event):
        """
        Maneja el evento cuando el usuario hace clic o da foco al campo.
        
        Comportamiento inteligente:
        - Si hay placeholder activo y el campo es editable: elimina placeholder
        - Si el campo es readonly: no hace cambios
        - Cambia el color del texto al color normal
        
        Args:
            event: Evento de tkinter (FocusIn o Button-1)
        """
        # Solo actuar si el placeholder está activo
        if self.placeholder_active:
            # Verificar si el campo permite edición
            # Nota: cget('state') retorna un objeto, no string directo
            if str(self.entry_search.cget('state')) == 'normal':
                # Limpiar placeholder y cambiar al modo de entrada normal
                self.entry_search.delete(0, "end")
                self.entry_search.config(foreground=self.text_color)
                self.placeholder_active = False
    
    def _on_focus_out(self, event):
        """
        Maneja el evento cuando el campo pierde el foco.
        
        Comportamiento:
        - Si el campo está vacío y es editable: restaura el placeholder
        - Si hay contenido: mantiene el contenido sin placeholder
        
        Args:
            event: Evento de tkinter (FocusOut)
        """
        # Solo actuar si el campo es editable y está vacío
        if str(self.entry_search.cget('state')) == 'normal' and not self.entry_search.get():
            # Restaurar placeholder visual
            self.entry_search.insert(0, self.placeholder_text)
            self.entry_search.config(foreground=self.placeholder_color)
            self.placeholder_active = True
    
    def get_search_text(self):
        """
        Obtiene el texto real ingresado por el usuario.
        
        Distingue entre placeholder y contenido real:
        - Si placeholder está activo: retorna string vacío
        - Si hay contenido real: retorna el texto actual
        
        Returns:
            str: Texto ingresado por el usuario (sin placeholder)
        """
        if self.placeholder_active:
            return ""
        return self.entry_search.get()
    
    def get(self):
        """
        Alias para get_search_text() para compatibilidad con Entry estándar.
        
        Permite usar este widget como reemplazo directo de tb.Entry
        sin cambiar el código cliente.
        
        Returns:
            str: Texto ingresado por el usuario
        """
        return self.get_search_text()
    
    def clear_search(self):
        """
        Limpia el contenido del campo y restaura el placeholder.
        
        Útil para:
        - Reset de formularios
        - Limpieza después de operaciones
        - Restauración a estado inicial
        """
        self.entry_search.delete(0, "end")
        self.entry_search.insert(0, self.placeholder_text)
        self.entry_search.config(foreground=self.placeholder_color)
        self.placeholder_active = True

    def set_text(self, text):
        """
        Establece contenido real en el campo, desactivando el placeholder.
        
        Usado para:
        - Llenar formularios con datos existentes
        - Establecer valores por defecto
        - Programar contenido desde el código
        
        Args:
            text: Texto a establecer (None o vacío restaura placeholder)
        """
        self.entry_search.delete(0, "end")
        if text and str(text).strip():
            # Hay contenido real: establecer y deshabilitar placeholder
            self.entry_search.insert(0, str(text))
            self.entry_search.config(foreground=self.text_color)
            self.placeholder_active = False
        else:
            # No hay contenido: restaurar placeholder
            self.entry_search.insert(0, self.placeholder_text)
            self.entry_search.config(foreground=self.placeholder_color)
            self.placeholder_active = True

    def set_placeholder_text(self, text):
        """
        Cambia el texto del placeholder dinámicamente.
        
        Si el placeholder está actualmente visible, lo actualiza inmediatamente.
        Útil para cambios contextuales del placeholder.
        
        Args:
            text (str): Nuevo texto para el placeholder
        """
        self.placeholder_text = text
        if self.placeholder_active:
            # Actualizar placeholder visible
            self.entry_search.delete(0, "end")
            self.entry_search.insert(0, self.placeholder_text)

    def pack(self, **kwargs):
        """
        Empaqueta el marco interno en el contenedor padre.
        
        Proporciona compatibilidad con el sistema de layout de tkinter.
        
        Args:
            **kwargs: Argumentos de empaquetado (side, fill, expand, etc.)
        """
        self.inner_frame.pack(**kwargs)
    
    def set_editable(self, editable=True):
        """
        Controla si el campo es editable o de solo lectura.
        
        Estados soportados:
        - Editable (normal): Usuario puede escribir y editar
        - Solo lectura (readonly): Usuario puede ver y seleccionar, no editar
        
        Mantiene colores apropiados para cada estado.
        
        Args:
            editable (bool): True para habilitar edición, False para readonly
        """
        if editable:
            # Campo editable - estado normal
            self.entry_search.config(state='normal')
            # Mantener colores según estado del placeholder
            if self.placeholder_active:
                self.entry_search.config(foreground=self.placeholder_color)
            else:
                self.entry_search.config(foreground=self.text_color)
        else:
            # Campo no editable - modo readonly (mantiene legibilidad)
            self.entry_search.config(state='readonly')
            # En modo readonly, mantener colores apropiados
            if not self.placeholder_active:
                self.entry_search.config(foreground=self.text_color)
    
    def focus_set(self):
        """
        Pone el foco en el Entry interno.
        
        Compatibilidad con Entry estándar para navegación por teclado.
        """
        self.entry_search.focus_set()
    
    def bind(self, event, callback):
        """
        Permite vincular eventos adicionales al Entry interno.
        
        Útil para:
        - Validaciones en tiempo real
        - Autocompletado
        - Eventos personalizados
        
        Args:
            event (str): Evento de tkinter (ej: '<KeyPress>', '<Return>')
            callback: Función a ejecutar cuando ocurre el evento
        """
        self.entry_search.bind(event, callback)
