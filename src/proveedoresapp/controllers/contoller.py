


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.search_frame.button_search.config(command=self.on_search)

    def on_search(self):
        search_query = self.view.search_frame.search_bar.get_search_text()
        # Aquí puedes agregar la lógica para manejar la búsqueda
        print(f"Buscando: {search_query}")
