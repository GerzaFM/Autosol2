import ttkbootstrap as tb
from ttkbootstrap.constants import *

from proveedoresapp.views.searchbar import SearchBar

class SearchFrame:
    def __init__(self, master):
        self.master = master
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=X, anchor=N, pady=(30, 10))

        self.inner_frame = tb.Frame(self.frame)
        self.inner_frame.pack()

        # SearchBar a la izquierda
        self.search_bar = SearchBar(self.inner_frame, "Buscar proveedor...", width=50)
        self.search_bar.inner_frame.pack(side=LEFT, padx=(0, 5))

        # Botón de búsqueda a la derecha del SearchBar
        self.button_search = tb.Button(self.inner_frame, text="🔍")
        self.button_search.pack(side=LEFT)

        self.switch_incomplete = tb.Checkbutton(self.inner_frame, text="Incompletos", bootstyle="success-round-toggle")
        self.switch_incomplete.pack(side=LEFT, padx=(15, 0))