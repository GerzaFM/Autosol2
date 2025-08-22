import ttkbootstrap as tb

from proveedoresapp.views.frame_search import SearchFrame
from proveedoresapp.views.frame_list import TreeFrame
from proveedoresapp.views.frame_buttons_list import ButtonsList
from proveedoresapp.views.frame_dataform import DataForm

class ProveedoreView:
    def __init__(self, master):
        
        self.search_frame = SearchFrame(master)
        self.tree_frame = TreeFrame(master)
        self.buttons_frame = ButtonsList(master)
        self.data_form = DataForm(master)