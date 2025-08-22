import ttkbootstrap as tb
from ttkbootstrap.constants import *

from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.controllers.contoller import Controller


class ProveedoresApp(tb.Frame):
    def __init__(self, master):
        super().__init__(master)


        self.model = None
        self.view = ProveedoreView(self)
        self.controller = Controller(self.model, self.view)

    def _create_widgets(self):
        # Aquí se pueden agregar más widgets específicos de la aplicación de proveedores
        pass
