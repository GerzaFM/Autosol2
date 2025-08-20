import ttkbootstrap as tb
from ttkbootstrap.constants import *

from proveedoresapp.views.frame_search import SearchFrame
from proveedoresapp.views.frame_list import TreeFrame
from proveedoresapp.views.frame_buttons_list import ButtonsList

class ProveedoresApp(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        # No hacer pack aquí, déjalo al padre que lo maneje
        
        self.search_frame = SearchFrame(self)
        self.tree_frame = TreeFrame(self)
        self.buttons_frame = ButtonsList(self)

        self._create_widgets()

    def _create_widgets(self):
        # Aquí se pueden agregar más widgets específicos de la aplicación de proveedores
        pass
