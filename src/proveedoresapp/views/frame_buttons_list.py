import ttkbootstrap as tb
from ttkbootstrap.constants import *

class ButtonsList:
    def __init__(self, master):
        self.master = master
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, fill=X, anchor=N, padx=30, pady=(0, 10))

        button_width = 12

        self.button_add = tb.Button(self.frame, text="Agregar", bootstyle="success", width=button_width)
        self.button_add.pack(side=RIGHT, padx=(5, 0))

        self.button_edit = tb.Button(self.frame, text="Editar", bootstyle="warning", width=button_width)
        self.button_edit.pack(side=RIGHT, padx=(5, 0))

        self.button_delete = tb.Button(self.frame, text="Eliminar", bootstyle="danger", width=button_width)
        self.button_delete.pack(side=RIGHT, padx=(5, 0))

        self.button_combine = tb.Button(self.frame, text="Combinar", bootstyle="info", width=button_width)
        self.button_combine.pack(side=RIGHT, padx=(5, 0))