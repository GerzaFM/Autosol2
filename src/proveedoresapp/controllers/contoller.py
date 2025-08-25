from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.models.model import ProveedorModel


class Controller:
    def __init__(self, model: ProveedorModel, view: ProveedoreView):
        self.model = model
        self.view = view

        self.proveedores = []

        self.load_proveedores()
        self.fill_list(self.proveedores)

    def load_proveedores(self):
        self.proveedores = self.model.obtener_todos()

    def fill_list(self, proveedores):
        table_data = [list(proveedor.values()) for proveedor in proveedores]
        self.view.fill_list(table_data)