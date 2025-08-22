import ttkbootstrap as tb
from ttkbootstrap.constants import *

class SearchBar:
    def __init__(self, master, placeholder="Ingrese un texto:", width=10):
        self.inner_frame = tb.Frame(master)
        
        self.entry_search = None
        self.placeholder_text = placeholder
        self.placeholder_active = True
        self.width = width

        self.create_widgets()

    def create_widgets(self):
        # Entry sin placeholdertext - implementamos placeholder manualmente
        self.entry_search = tb.Entry(
            self.inner_frame, 
            font=("Segoe UI", 10),
            foreground="gray",
            width=self.width
        )
        self.entry_search.pack(side=LEFT, padx=10)
        
        # Insertar texto placeholder
        self.entry_search.insert(0, self.placeholder_text)
        
        # Eventos para manejar el placeholder
        self.entry_search.bind('<FocusIn>', self._on_entry_click)
        self.entry_search.bind('<FocusOut>', self._on_focus_out)
    
    def _on_entry_click(self, event):
        """Elimina el placeholder cuando el usuario hace clic en el entry."""
        if self.placeholder_active:
            self.entry_search.delete(0, "end")
            self.entry_search.config(foreground="black")
            self.placeholder_active = False
    
    def _on_focus_out(self, event):
        """Restaura el placeholder si el entry está vacío."""
        if not self.entry_search.get():
            self.entry_search.insert(0, self.placeholder_text)
            self.entry_search.config(foreground="gray")
            self.placeholder_active = True
    
    def get_search_text(self):
        """Obtiene el texto de búsqueda (sin el placeholder)."""
        if self.placeholder_active:
            return ""
        return self.entry_search.get()
    
    def clear_search(self):
        """Limpia el texto de búsqueda y restaura el placeholder."""
        self.entry_search.delete(0, "end")
        self.entry_search.insert(0, self.placeholder_text)
        self.entry_search.config(foreground="gray")
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
