import ttkbootstrap as tb
from ttkbootstrap.constants import *

try:
    from proveedoresapp.views.searchbar import SearchBar
except ImportError:
    from searchbar import SearchBar
finally:
    if SearchBar is None:
        class SearchBar:
            def __init__(self, master, placeholder="", width=100):
                self.entry = tb.Entry(master, bootstyle=PRIMARY, width=width)
                self.entry.insert(0, placeholder)
                self.entry.pack(side=LEFT, fill=X, padx=5, pady=5)


class DataForm:
    def __init__(self, master):
        self.master = master
        self.frame = tb.Frame(master)
        self.frame.pack(side=TOP, anchor=N, pady=(30, 10), expand=False)

        self.button_cancelar = None
        self.button_guardar = None

        self.create_form()
        self.create_buttons()

    def create_form(self):
        frame_top = tb.Frame(self.frame)
        frame_top.pack(side=TOP, fill=X, padx=15, pady=5)

        frame_midle = tb.Frame(self.frame)
        frame_midle.pack(side=TOP, fill=X, padx=15, pady=5)

        frame_bottom = tb.Frame(self.frame)
        frame_bottom.pack(side=TOP, fill=X, padx=15, pady=5)

        small = 15
        medium = 30
        large = 50
        self.entry_codigo = SearchBar(frame_top, placeholder="Codigo quiter", width=small)
        self.entry_nombre = SearchBar(frame_top, placeholder="Nombre fiscal", width=large)
        self.entry_email = SearchBar(frame_top, placeholder="Email", width=medium)
        self.entry_nombre_contacto = SearchBar(frame_top, placeholder="Nombre contacto", width=medium)


        self.entry_rfc = SearchBar(frame_midle , placeholder="RFC", width=small)
        self.entry_nombre_quiter = SearchBar(frame_midle, placeholder="Nombre quiter", width=large)
        self.entry_telefono = SearchBar(frame_midle, placeholder="Telefono", width=medium)

        # Empaquetar los widgets
        self.entry_codigo.pack(side=LEFT, fill=X, padx=5, pady=5)
        self.entry_nombre.pack(side=LEFT, fill=X, padx=5, pady=5)   
        self.entry_email.pack(side=LEFT, fill=X, padx=5, pady=5) 
        self.entry_nombre_contacto.pack(side=LEFT, fill=X, padx=5, pady=5)

        self.entry_rfc.pack(side=LEFT, fill=X, padx=5, pady=5)       
        self.entry_nombre_quiter.pack(side=LEFT, fill=X, padx=5, pady=5)
        self.entry_telefono.pack(side=LEFT, fill=X, padx=5, pady=5)


    def create_buttons(self):
        frame_bottom = tb.Frame(self.frame)
        frame_bottom.pack(side=TOP, fill=X, padx=15, pady=5)

        self.button_guardar = tb.Button(frame_bottom, text="Guardar", bootstyle=SUCCESS,width=12)
        self.button_guardar.pack(side=RIGHT, padx=(5, 15), pady=(0, 5))

        self.button_cancelar = tb.Button(frame_bottom, text="Cancelar", bootstyle=DANGER,width=12)
        self.button_cancelar.pack(side=RIGHT, padx=(5, 0), pady=(0, 5))


if __name__ == "__main__":
    import tkinter as tk
    import ttkbootstrap as tb

    root = tb.Window(themename="flatly")
    root.title("Prueba DataForm")

    # Instanciar y mostrar el formulario
    app = DataForm(root)
    root.mainloop()


