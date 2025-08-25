import ttkbootstrap as tb
from ttkbootstrap.constants import *

class SearchBar:
    def __init__(self, master, placeholder="Ingrese un texto:", width=10):
        self.inner_frame = tb.Frame(master)
        
        self.entry_search = None
        self.placeholder_text = placeholder
        self.placeholder_active = True
        self.width = width
        
        # Detectar el tema para ajustar colores
        self._setup_colors()

        self.create_widgets()
    
    def _setup_colors(self):
        """Configura los colores según el tema actual."""
        try:
            # Intentar obtener el tema actual
            style = tb.Style()
            theme_name = style.theme.name if hasattr(style, 'theme') else 'flatly'
            
            # Configurar colores según el tema
            if 'dark' in theme_name.lower():
                # Tema oscuro
                self.placeholder_color = "gray"
                self.text_color = "white"
                self.disabled_color = "#555555"  # Gris oscuro para campos deshabilitados
            else:
                # Tema claro
                self.placeholder_color = "gray"
                self.text_color = "black"
                self.disabled_color = "#999999"  # Gris claro para campos deshabilitados
        except:
            # Fallback por defecto
            self.placeholder_color = "gray"
            self.text_color = "black"
            self.disabled_color = "#999999"

    def create_widgets(self):
        # Entry sin placeholdertext - implementamos placeholder manualmente
        self.entry_search = tb.Entry(
            self.inner_frame, 
            font=("Segoe UI", 10),
            foreground=self.placeholder_color,
            width=self.width
        )
        self.entry_search.pack(side=LEFT, padx=10)
        
        # Insertar texto placeholder
        self.entry_search.insert(0, self.placeholder_text)
        
        # Eventos para manejar el placeholder
        self.entry_search.bind('<FocusIn>', self._on_entry_click)
        self.entry_search.bind('<Button-1>', self._on_entry_click)
        self.entry_search.bind('<FocusOut>', self._on_focus_out)
    
    def _on_entry_click(self, event):
        """Elimina el placeholder cuando el usuario hace clic en el entry."""
        # Actuar si el placeholder está activo
        if self.placeholder_active:
            # Solo cambiar si el campo es editable
            if str(self.entry_search.cget('state')) == 'normal':
                self.entry_search.delete(0, "end")
                self.entry_search.config(foreground=self.text_color)
                self.placeholder_active = False
    
    def _on_focus_out(self, event):
        """Restaura el placeholder si el entry está vacío."""
        # Solo actuar si el campo es editable y está vacío
        if str(self.entry_search.cget('state')) == 'normal' and not self.entry_search.get():
            self.entry_search.insert(0, self.placeholder_text)
            self.entry_search.config(foreground=self.placeholder_color)
            self.placeholder_active = True
    
    def get_search_text(self):
        """Obtiene el texto de búsqueda (sin el placeholder)."""
        if self.placeholder_active:
            return ""
        return self.entry_search.get()
    
    def get(self):
        """Alias para get_search_text() para compatibilidad."""
        return self.get_search_text()
    
    def clear_search(self):
        """Limpia el texto de búsqueda y restaura el placeholder."""
        self.entry_search.delete(0, "end")
        self.entry_search.insert(0, self.placeholder_text)
        self.entry_search.config(foreground=self.placeholder_color)
        self.placeholder_active = True

    def set_text(self, text):
        """Establece texto real en el campo, desactivando el placeholder."""
        self.entry_search.delete(0, "end")
        if text and str(text).strip():
            self.entry_search.insert(0, str(text))
            self.entry_search.config(foreground=self.text_color)
            self.placeholder_active = False
        else:
            self.entry_search.insert(0, self.placeholder_text)
            self.entry_search.config(foreground=self.placeholder_color)
            self.placeholder_active = True

    def set_placeholder_text(self, text):
        """Establece el texto del placeholder."""
        self.placeholder_text = text
        if self.placeholder_active:
            self.entry_search.delete(0, "end")
            self.entry_search.insert(0, self.placeholder_text)

    def pack(self, **kwargs):
        """Empaqueta el marco interno en el contenedor padre."""
        self.inner_frame.pack(**kwargs)
    
    def set_editable(self, editable=True):
        """Establece si el campo es editable o no."""
        if editable:
            # Campo editable - habilitar
            self.entry_search.config(state='normal')
            # Mantener el color según el estado actual del placeholder
            if self.placeholder_active:
                self.entry_search.config(foreground=self.placeholder_color)
            else:
                self.entry_search.config(foreground=self.text_color)
        else:
            # Campo no editable - deshabilitar
            self.entry_search.config(state='readonly')  # Cambié de 'disabled' a 'readonly' para mantener legibilidad
            # En modo readonly, mantener colores apropiados
            if not self.placeholder_active:
                self.entry_search.config(foreground=self.text_color)
    
    def focus_set(self):
        """Pone el foco en el entry."""
        self.entry_search.focus_set()
    
    def bind(self, event, callback):
        """Permite vincular eventos al entry."""
        self.entry_search.bind(event, callback)
