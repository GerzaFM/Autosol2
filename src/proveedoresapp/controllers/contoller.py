from proveedoresapp.views.main_view import ProveedoreView
from proveedoresapp.models.model import ProveedorModel


class Controller:
    def __init__(self, model: ProveedorModel, view: ProveedoreView):
        self.model = model
        self.view = view

        #self.view.search_frame.button_search.config(command=self.on_search)
        #self.view.button_search.config(command=self.on_search)
        #self.view.fill_data(["Hp"])

    def on_search(self):
        search_query = self.view.search_frame.search_bar.get_search_text()
        # Aquí puedes agregar la lógica para manejar la búsqueda
        print(f"Buscando: {search_query}")
