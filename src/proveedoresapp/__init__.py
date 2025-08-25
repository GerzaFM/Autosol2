import ttkbootstrap as tb
from ttkbootstrap.constants import *

from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.controllers.contoller import Controller
from proveedoresapp.models.model import ProveedorModel


class ProveedoresApp(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.model = ProveedorModel()
        self.view = ProveedoreView(self)  # Ahora pasa 'self' como padre
        self.controller = Controller(self.model, self.view)
        
        # Hacer que este frame ocupe todo el espacio disponible
        self.pack(fill='both', expand=True)

